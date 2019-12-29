from __future__ import annotations

import sys
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List, Optional

from sites import tripadvisor as ta
from sites import google_maps as gm
from sites import restaurant as rt
from sites.restaurant import Restaurant, CombinedRestaurant

api_key: str = sys.argv[1]
town: str = "nice france"

def get_combined_restaurant(restaurant: Restaurant, optional_restaurant: Optional[Restaurant]) -> CombinedRestaurant:
    all_restaurants: List[Restaurant] = [restaurant]
    if optional_restaurant:
        all_restaurants.append(optional_restaurant)
    return CombinedRestaurant(all_restaurants)

with ThreadPoolExecutor(max_workers=2) as executor:
    arguments = (town, api_key, 300)
    tripadvisor = executor.submit(ta.get_restaurants, *arguments)
    google_maps = executor.submit(gm.get_restaurants, *arguments)
tripadvisor_restaurants: List[Restaurant] = tripadvisor.result()
google_maps_restaurants: List[Restaurant] = google_maps.result()

tripadvisor_restaurants = sorted(tripadvisor_restaurants, key=lambda restaurant: restaurant.average_rating(), reverse=True)
google_maps_restaurants = sorted(google_maps_restaurants, key=lambda restaurant: restaurant.average_rating(), reverse=True)

combined_restaurants: List[CombinedRestaurant] = []
for restaurant in google_maps_restaurants[:30]:
    tripadvisor: Restaurant = ta.get_same_restaurant(restaurant, tripadvisor_restaurants)
    combined_restaurants.append(get_combined_restaurant(restaurant, tripadvisor))

for restaurant in tripadvisor_restaurants[:30]:
    google_maps: Restaurant = gm.get_same_restaurant(restaurant, google_maps_restaurants)
    combined_restaurants.append(get_combined_restaurant(restaurant, google_maps))


for restaurant in combined_restaurants:
    score: float = rt.get_score(restaurant, combined_restaurants)
    print(f"name: {restaurant.all_sites[0].name()} size: {len(restaurant.all_sites)}, score: {score}")





