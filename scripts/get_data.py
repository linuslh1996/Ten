from __future__ import annotations

import sys
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional, Callable

from sites.rating_sites import GoogleMaps, TripAdvisor, RatingSite, SiteType
from sites.restaurant import Restaurant, CombinedRestaurant
import sites.utils as utils


def get_combined_restaurant(restaurant: Restaurant, optional_restaurant: Optional[Restaurant]) -> CombinedRestaurant:
    all_restaurants: List[Restaurant] = [restaurant]
    if optional_restaurant:
        all_restaurants.append(optional_restaurant)
    return CombinedRestaurant(all_restaurants)

def removed_duplicates(combined_restaurants: List[CombinedRestaurant]) -> List[Restaurant]:
    without_duplicates: List[Restaurant] = []
    for restaurant in combined_restaurants:
        if restaurant.get_name() not in [restaurant.get_name() for restaurant in without_duplicates]:
            without_duplicates.append(restaurant)
    return without_duplicates

def combine_restaurant_info(restaurant: Restaurant, already_loaded: List[List[Restaurant]], sites: List[RatingSite], town: str) -> CombinedRestaurant:
    all_infos_for_restaurant: List[Restaurant] = [restaurant]
    for i, site in enumerate(sites):
        if restaurant.get_site() == site.get_site_type():
            continue
        site_info_for_restaurant: Optional[Restaurant] = site.get_same_restaurant(restaurant, already_loaded[i], town)
        if not site_info_for_restaurant:
            continue
        all_infos_for_restaurant.append(site_info_for_restaurant)
    return CombinedRestaurant(all_infos_for_restaurant)


# Init
api_key: str = sys.argv[1]
town: str = "nice france"
google_maps: GoogleMaps = GoogleMaps(api_key)
trip_advisor: TripAdvisor = TripAdvisor(api_key)
sites: List[RatingSite] = [google_maps, trip_advisor]
# Query Restaurants
with ThreadPoolExecutor(max_workers=2) as executor:
    get_restaurants: Callable = lambda rating_site: rating_site.get_restaurants(town, 100)
    restaurant_results: List[List[Restaurant]] = executor.map(get_restaurants, sites)
# Combine Info From The Different Sites
combined_restaurants: List[CombinedRestaurant] = []
for site_result in restaurant_results:
    sorted_by_average_rating = sorted(site_result, key=lambda restaurant: restaurant.average_rating(), reverse=True)
    relevant_restaurants: List[Restaurant] = sorted_by_average_rating[:20]
    completed_infos: List[CombinedRestaurant] = [combine_restaurant_info(restaurant, restaurant_results, sites, town)
                                      for restaurant in relevant_restaurants]
    combined_restaurants += completed_infos
# Filter
only_with_full_info: List[CombinedRestaurant] = [restaurant for restaurant in combined_restaurants if len(restaurant.all_sites) == 2]
duplicates_removed: List[CombinedRestaurant] = removed_duplicates(only_with_full_info)
sorted_by_score = sorted(duplicates_removed, key=lambda restaurant: restaurant.get_score(sorted_by_score), reverse=True)
# Print Results
for combined_restaurant in sorted_by_score[:10]:
    score: float = combined_restaurant.get_score(combined_restaurants)
    reviews: List[str] = google_maps.get_reviews(combined_restaurant.get_from_site(SiteType.GOOGLE_MAPS))
    best_review: str = utils.choose_best_review(reviews)
    print(f"name: {combined_restaurant.get_name()} size: {len(combined_restaurant.all_sites)}, score: {score}")
    print(best_review)







