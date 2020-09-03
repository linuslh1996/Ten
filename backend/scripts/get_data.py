from __future__ import annotations

from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import dataclass
from typing import List, Optional, Callable, Tuple

from psycopg2.sql import SQL
from tqdm import tqdm
import os

from sites.database import PostgresDatabase
from sites.rating_sites import GoogleMaps, TripAdvisor, RatingSite
from sites.restaurant import RestaurantResult, CombinedRestaurant, SiteType, GoogleMapsResult, TripAdvisorResult, \
    get_table_metadata
import logging
from pandas import DataFrame, read_csv

from sites.utils import timeout


@dataclass
class Result:
    google_maps_restaurant: GoogleMapsResult
    trip_advisor_restaurant: TripAdvisorResult
    combined: CombinedRestaurant

# API Calls

def load_town_results(town: str, country: str) -> List[Result]:
    # Init
    search_string: str = town + " " + country
    google_maps: GoogleMaps = GoogleMaps(API_KEY)
    trip_advisor: TripAdvisor = TripAdvisor(API_KEY)
    sites: List[RatingSite] = [google_maps, trip_advisor]
    # Query Restaurants
    with ThreadPoolExecutor(max_workers=2) as executor:
        get_restaurants: Callable = lambda rating_site: rating_site.get_restaurants(search_string, 200)
        restaurant_results: List[List[RestaurantResult]] = list(executor.map(get_restaurants, sites))
    print("Got Results")
    # Combine Info From The Different Sites
    all_restaurants: List[List[RestaurantResult]] = []
    for site_result in restaurant_results:
        sorted_by_score = sorted(site_result, key=lambda restaurant: restaurant.get_score(site_result), reverse=True)
        relevant_restaurants: List[RestaurantResult] = sorted_by_score[:60]
        completed_infos: List[List[RestaurantResult]] = [combine_restaurant_info(restaurant, restaurant_results, sites, search_string)
                                                         for restaurant in relevant_restaurants]
        all_restaurants += completed_infos
    print("Combined Restaurants")
    # Filter
    only_with_full_info: List[List[RestaurantResult]] = [restaurant_sites for restaurant_sites in all_restaurants if
                                                         len(restaurant_sites) == 2]
    duplicates_removed: List[List[RestaurantResult]] = removed_duplicates(only_with_full_info)
    sorted_by_combined_score: List[List[RestaurantResult]] = sorted(duplicates_removed,
                             key=lambda restaurant_sites: get_score(restaurant_sites, duplicates_removed), reverse=True)
    results: List[Result] = []
    # Create Result
    for i, restaurant_sites in enumerate(tqdm(sorted_by_combined_score[:1])):
        google_maps_restaurant, trip_advisor_restaurant = get_typed_restaurants(restaurant_sites)
        number_of_restaurants_to_load_more_detailed_info_to: int = 25
        if i < number_of_restaurants_to_load_more_detailed_info_to:
            google_maps_restaurant = google_maps.complete_restaurant_info(google_maps_restaurant)
        combined_restaurant: CombinedRestaurant = CombinedRestaurant(town=town, country=country, google_maps_link=google_maps_restaurant.link,
                                                                     trip_advisor_link=trip_advisor_restaurant.link)
        results.append(Result(google_maps_restaurant, trip_advisor_restaurant, combined_restaurant))
    return results

# Processing Methods For Restaurant Combination

def removed_duplicates(all_restaurants: List[List[RestaurantResult]]) -> List[List[RestaurantResult]]:
    without_duplicates: List[List[RestaurantResult]] = []
    for all_sites in all_restaurants:
        if get_name(all_sites) not in [get_name(restaurant) for restaurant in without_duplicates]:
            without_duplicates.append(all_sites)
    return without_duplicates

def combine_restaurant_info(restaurant: RestaurantResult, already_loaded: List[List[RestaurantResult]], sites: List[RatingSite], town: str) -> List[RestaurantResult]:
    all_infos_for_restaurant: List[RestaurantResult] = [restaurant]
    for i, site in enumerate(sites):
        if restaurant.get_site_provider() == site.get_site_type():
            continue
        site_info_for_restaurant: Optional[RestaurantResult] = site.get_same_restaurant(restaurant, already_loaded[i], town)
        if not site_info_for_restaurant:
            continue
        all_infos_for_restaurant.append(site_info_for_restaurant)
    return all_infos_for_restaurant

def get_typed_restaurants(restaurant_sites: List[RestaurantResult]) -> Tuple[GoogleMapsResult, TripAdvisorResult]:
    # noinspection PyTypeChecker
    google_maps_restaurant: GoogleMapsResult = get_from_site(restaurant_sites, SiteType.GOOGLE_MAPS)
    # noinspection PyTypeChecker
    trip_advisor_restaurant: TripAdvisorResult = get_from_site(restaurant_sites, SiteType.TRIP_ADVISOR)
    return (google_maps_restaurant, trip_advisor_restaurant)

def get_from_site(restaurant_sites: List[RestaurantResult], site: SiteType) -> RestaurantResult:
    info_from_site: RestaurantResult = next(filter(lambda restaurant: restaurant.get_site_provider() == site, restaurant_sites), None)
    assert info_from_site is not None
    return info_from_site

def has_entry_on_site(restaurant_sites: List[RestaurantResult], site: SiteType) -> bool:
    return next(filter(lambda restaurant: restaurant.site == site, restaurant_sites), None) is not None

def get_score(restaurant_sites: List[RestaurantResult], all_restaurants: List[List[RestaurantResult]]) -> float:
    total_score: float = 0
    for i in range(len(restaurant_sites)):
        restaurant_from_site: RestaurantResult = restaurant_sites[i]
        total_score += restaurant_from_site.get_score(all_restaurants[i])
    mean_score: float = total_score / len(restaurant_sites)
    return mean_score

def get_name(restaurant_sites: List[RestaurantResult]) -> str:
    return get_from_site(restaurant_sites, SiteType.GOOGLE_MAPS).name

def _change_shape(results: List[Result]) -> Tuple[List[GoogleMapsResult], List[TripAdvisorResult], List[CombinedRestaurant]]:
    google_maps_result: List[GoogleMapsResult] = [result.google_maps_restaurant for result in results]
    trip_advisor_result: List[TripAdvisorResult] = [result.trip_advisor_restaurant for result in results]
    combined: List[CombinedRestaurant] = [result.combined for result in results]
    return google_maps_result, trip_advisor_result, combined


if __name__ == "__main__":
    API_KEY: str = os.environ["API_KEY"]
    DATABASE_URL = os.environ["DATABASE_URL"]
    # Start Postgres
    meta_information = get_table_metadata()
    postgres_db = PostgresDatabase(DATABASE_URL)
    postgres_db.initialize_tables(DATABASE_URL, meta_information)
    # Crawl Data For German Towns
    german_towns: List[str] = list(read_csv("data/towns_germany.csv")["name"]) # The towns are already sorted by population

    for i, town in enumerate(german_towns[25:200]):
        print(f"processing town {i}: {town}")
        try:
            with timeout(seconds=300):
                results = load_town_results(town, "Deutschland")
                google_maps_results, trip_advisor_results, restaurants = _change_shape(results)
                postgres_db.convert_to_db_entry(google_maps_results, "google_maps").upsert()
                #postgres_db.convert_to_db_entry(trip_advisor_results, "trip_advisor").upsert()
                #postgres_db.convert_to_db_entry(restaurants, "restaurants").upsert()
        except Exception:
            logging.exception(f"Error for town {town}. Continuing with next town")





