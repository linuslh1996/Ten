from __future__ import annotations

import sys
import time
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional, Callable

from starlette.middleware.cors import CORSMiddleware

from sites.rating_sites import GoogleMaps, TripAdvisor, RatingSite
from sites.restaurant import Restaurant, CombinedRestaurant, SiteType
import sites.utils as utils
from fastapi import FastAPI
import uvicorn

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key: str = sys.argv[1]

# API Calls

@app.get("/restaurants")
def load_town_results(town: str):
    # Init
    google_maps: GoogleMaps = GoogleMaps(api_key)
    trip_advisor: TripAdvisor = TripAdvisor(api_key)
    sites: List[RatingSite] = [google_maps, trip_advisor]
    # Query Restaurants
    with ThreadPoolExecutor(max_workers=2) as executor:
        get_restaurants: Callable = lambda rating_site: rating_site.get_restaurants(town, 200)
        restaurant_results: List[List[Restaurant]] = list(executor.map(get_restaurants, sites))
    # Combine Info From The Different Sites
    all_restaurants: List[List[Restaurant]] = []
    for site_result in restaurant_results:
        sorted_by_score = sorted(site_result, key=lambda restaurant: restaurant.get_score(site_result), reverse=True)
        relevant_restaurants: List[Restaurant] = sorted_by_score[:20]
        completed_infos: List[List[Restaurant]] = [combine_restaurant_info(restaurant, restaurant_results, sites, town)
                                                   for restaurant in relevant_restaurants]
        all_restaurants += completed_infos
    # Filter
    only_with_full_info: List[List[Restaurant]] = [restaurant_sites for restaurant_sites in all_restaurants if
                                                   len(restaurant_sites) == 2]
    duplicates_removed: List[List[Restaurant]] = removed_duplicates(only_with_full_info)
    sorted_by_score = sorted(duplicates_removed,
                             key=lambda restaurant_sites: get_score(restaurant_sites, duplicates_removed), reverse=True)
    as_combined_restaurants: List[CombinedRestaurant] = [load_combined_restaurant(restaurant_sites, duplicates_removed, google_maps)
                                                         for restaurant_sites in sorted_by_score[:10]]
    return as_combined_restaurants

# Processing Methods For Restaurant Combination

def load_combined_restaurant(restaurant_sites: List[Restaurant], all_restaurants: List[List[Restaurant]], google_maps: GoogleMaps):
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

def get_from_site(restaurant_sites: List[Restaurant], site: SiteType, ) -> Restaurant:
    info_from_site: Restaurant = next(filter(lambda restaurant: restaurant.site == site, restaurant_sites), None)
    assert info_from_site is not None
    return info_from_site

def has_entry_on_site(restaurant_sites: List[Restaurant], site: SiteType) -> bool:
    return next(filter(lambda restaurant: restaurant.site == site, restaurant_sites), None) is not None

def get_score(restaurant_sites: List[Restaurant], all_restaurants: List[List[Restaurant]]) -> float:
    total_score: float = 0
    for i in range(len(restaurant_sites)):
        restaurant_from_site: Restaurant = restaurant_sites[i]
        total_score += restaurant_from_site.get_score(all_restaurants[i])
    mean_score: float = total_score / len(restaurant_sites)
    return mean_score

def get_name(restaurant_sites: List[Restaurant]) -> str:
    return get_from_site(restaurant_sites, SiteType.GOOGLE_MAPS).name


if __name__ == "__main__":
    uvicorn.run(app, port=5000)





