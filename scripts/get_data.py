from __future__ import annotations

import copy
import sys
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional

from sites import tripadvisor as ta
from sites import google_maps as gm
from sites import selector as sel
from sites.restaurant import Restaurant, CombinedRestaurant, RatingSite


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


api_key: str = sys.argv[1]
town: str = "nice france"

with ThreadPoolExecutor(max_workers=2) as executor:
    arguments = (town, api_key, 100)
    tripadvisor = executor.submit(ta.get_restaurants, *arguments)
    google_maps = executor.submit(gm.get_restaurants, *arguments)
tripadvisor_restaurants: List[Restaurant] = tripadvisor.result()
google_maps_restaurants: List[Restaurant] = google_maps.result()

tripadvisor_restaurants = sorted(tripadvisor_restaurants, key=lambda restaurant: restaurant.average_rating(), reverse=True)
google_maps_restaurants = sorted(google_maps_restaurants, key=lambda restaurant: restaurant.average_rating(), reverse=True)

combined_restaurants: List[CombinedRestaurant] = []
for restaurant in google_maps_restaurants[:20]:
    tripadvisor: Restaurant = ta.get_same_restaurant(restaurant, tripadvisor_restaurants)
    combined_restaurants.append(get_combined_restaurant(restaurant, tripadvisor))

for restaurant in tripadvisor_restaurants[:20]:
    google_maps: Restaurant = gm.get_same_restaurant(restaurant, google_maps_restaurants, town, api_key)
    combined_restaurants.append(get_combined_restaurant(restaurant, google_maps))

combined_restaurants = [restaurant for restaurant in combined_restaurants if len(restaurant.all_sites) == 2]
combined_restaurants = sorted(combined_restaurants, key=lambda restaurant: restaurant.get_score(combined_restaurants), reverse=True)
combined_restaurants = removed_duplicates(combined_restaurants)

combined_restaurant: CombinedRestaurant
for combined_restaurant in combined_restaurants[:10]:
    score: float = combined_restaurant.get_score(combined_restaurants)
    reviews: List[str] = gm.get_reviews(combined_restaurant.get_from_site(RatingSite.GOOGLE_MAPS), api_key)
    best_review: str = sel.choose_best_review(reviews)
    print(f"name: {combined_restaurant.get_name()} size: {len(combined_restaurant.all_sites)}, score: {score}")
    print(best_review)







