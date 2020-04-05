from __future__ import annotations

import json
import sys
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional, Callable

from sites.rating_sites import GoogleMaps, TripAdvisor, RatingSite
from sites.restaurant import Restaurant, CombinedRestaurant, SiteType
import sites.utils as utils

def load_combined_restaurant(restaurant_sites: List[Restaurant], all_restaurants: List[List[Restaurant]]):
    score: float = get_score(restaurant_sites, all_restaurants)
    reviews: List[str] = google_maps.get_reviews(get_from_site(restaurant_sites, SiteType.GOOGLE_MAPS))
    best_review: str = utils.choose_best_review(reviews)
    name: str = get_name(restaurant_sites)
    combined_restaurant: CombinedRestaurant = CombinedRestaurant(name, restaurant_sites, best_review, score)
    # Google Maps Handles not so many requests per second
    time.sleep(1)
    return combined_restaurant


def removed_duplicates(all_restaurants: List[List[Restaurant]]) -> List[List[Restaurant]]:
    without_duplicates: List[List[Restaurant]] = []
    for all_sites in all_restaurants:
        if get_name(all_sites) not in [get_name(restaurant) for restaurant in without_duplicates]:
            without_duplicates.append(all_sites)
    return without_duplicates

def combine_restaurant_info(restaurant: Restaurant, already_loaded: List[List[Restaurant]], sites: List[RatingSite], town: str) -> List[Restaurant]:
    all_infos_for_restaurant: List[Restaurant] = [restaurant]
    for i, site in enumerate(sites):
        if restaurant.site == site.get_site_type():
            continue
        site_info_for_restaurant: Optional[Restaurant] = site.get_same_restaurant(restaurant, already_loaded[i], town)
        if not site_info_for_restaurant:
            continue
        all_infos_for_restaurant.append(site_info_for_restaurant)
    return all_infos_for_restaurant

# Processing Methods For Restaurant Combination

def get_from_site(restaurant_sites: List[Restaurant], site: SiteType, ) -> Restaurant:
    info_from_site: Restaurant = next(filter(lambda restaurant: restaurant.site == site, restaurant_sites), None)
    assert info_from_site is not None
    return info_from_site

def has_entry_on_site(restaurant_sites: List[Restaurant], site: SiteType) -> bool:
    return next(filter(lambda restaurant: restaurant.site == site, restaurant_sites), None) is not None

def get_combined_amount_of_reviews(restaurant_sites: List[Restaurant]):
    total_amount: int = 0
    for site in restaurant_sites:
        total_amount += site.number_of_reviews
    return total_amount

def get_combined_rating(restaurant_sites: List[Restaurant]):
    combined_rating: float = 0
    for site in restaurant_sites:
        combined_rating += site.rating
    return combined_rating / len(restaurant_sites)

def get_score(restaurant_sites: List[Restaurant], all_restaurants: List[List[Restaurant]]) -> float:
    max_amount_of_reviews: int = max([get_combined_amount_of_reviews(restaurant) for restaurant in all_restaurants])
    popularity_score: float = get_combined_amount_of_reviews(restaurant_sites) / max_amount_of_reviews * 10
    rating_score: float = (get_combined_rating(restaurant_sites) - 8) * 5
    total_score = 0.4 * popularity_score + 0.6 * rating_score
    return total_score

def get_name(restaurant_sites: List[Restaurant]) -> str:
    return get_from_site(restaurant_sites, SiteType.GOOGLE_MAPS).name


# Init
api_key: str = sys.argv[1]
town: str = "potsdam germany"
google_maps: GoogleMaps = GoogleMaps(api_key)
trip_advisor: TripAdvisor = TripAdvisor(api_key)

sites: List[RatingSite] = [google_maps, trip_advisor]
# Query Restaurants
with ThreadPoolExecutor(max_workers=2) as executor:
    get_restaurants: Callable = lambda rating_site: rating_site.get_restaurants(town, 100)
    restaurant_results: List[List[Restaurant]] = [get_restaurants(rating_site) for rating_site in sites]
# Combine Info From The Different Sites
all_restaurants: List[List[Restaurant]] = []
for site_result in restaurant_results:
    sorted_by_average_rating = sorted(site_result, key=lambda restaurant: restaurant.rating, reverse=True)
    relevant_restaurants: List[Restaurant] = sorted_by_average_rating[:20]
    completed_infos: List[List[Restaurant]] = [combine_restaurant_info(restaurant, restaurant_results, sites, town)
                                      for restaurant in relevant_restaurants]
    all_restaurants += completed_infos
# Filter
only_with_full_info: List[List[Restaurant]] = [restaurants_sites for restaurants_sites in all_restaurants if len(restaurants_sites) == 2]
duplicates_removed: List[List[Restaurant]] = removed_duplicates(only_with_full_info)
sorted_by_score = sorted(duplicates_removed, key=lambda restaurant_sites: get_score(restaurant_sites, duplicates_removed), reverse=True)
as_combined_restaurants: List[CombinedRestaurant] = [load_combined_restaurant(restaurant_sites, sorted_by_score)
                                                    for restaurant_sites in sorted_by_score[:10]]
# Print Results
for combined_restaurant in as_combined_restaurants:
    print(f"name: {combined_restaurant.name} size: {len(combined_restaurant.all_sites)}, score: {combined_restaurant.score}")
    print(combined_restaurant.review)

json.dumps([restaurant.to_dict() for restaurant in as_combined_restaurants])



