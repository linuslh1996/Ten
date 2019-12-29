from __future__ import annotations

import sys
from concurrent.futures.thread import ThreadPoolExecutor
from typing import List

import numpy as np
from textdistance import ratcliff_obershelp

from sites import tripadvisor as ta
from sites import google_maps as gm
from sites import restaurant as rt
from sites.restaurant import Restaurant, CombinedRestaurant

api_key: str = sys.argv[1]
town: str = "nice france"

with ThreadPoolExecutor(max_workers=2) as executor:
    arguments = (town, api_key, 500)
    tripadvisor = executor.submit(ta.get_restaurants, *arguments)
    google_maps = executor.submit(gm.get_restaurants, *arguments)
tripadvisor = tripadvisor.result()
google_maps = google_maps.result()


combined_restaurants: List[CombinedRestaurant] = []
for google_restaurant in google_maps:
    # Check Out If Available On TripAdvisor
    name: str = google_restaurant.name().lower()
    similarities: List[float] = [ratcliff_obershelp.normalized_distance(name, trip.name().lower()) for trip in tripadvisor]
    # noinspection PyTypeChecker
    smallest_index: int = np.argmin(similarities)
    similar_restaurant: Restaurant = tripadvisor[smallest_index]
    threshold_for_dissimilar_names: float = 0.25
    # Build CombinedRestaurant
    all_sites_for_restaurant = [google_restaurant]
    if similarities[smallest_index] < threshold_for_dissimilar_names:
        all_sites_for_restaurant.append(similar_restaurant)
    combined_restaurants.append(CombinedRestaurant(all_sites_for_restaurant))


for restaurant in combined_restaurants:
    score: float = rt.get_score(restaurant, combined_restaurants)
    print(f"name: {restaurant.all_sites[0].name()} size: {len(restaurant.all_sites)}, score: {score}")





