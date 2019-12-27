from __future__ import annotations


from pathlib import Path
import json
from typing import List
import sys

import requests
import re
from bs4 import BeautifulSoup, ResultSet
from multiprocessing.dummy import Pool as ThreadPool
from textdistance import ratcliff_obershelp
import numpy as np

from restaurant import Restaurant, RatingSite
import google_maps as gm
import tripadvisor as ta

class CombinedRestaurant:

    def __init__(self, restaurant_from_all_sites: List[Restaurant]):
        self.all_sites: List[Restaurant] = restaurant_from_all_sites

    def get_from_site(self, site: RatingSite) -> Restaurant:
        info_from_site: Restaurant = next(filter(lambda restaurant: restaurant.site == site, self.all_sites), None)
        assert info_from_site is not None
        return info_from_site

    def has_entry_on_site(self, site: RatingSite) -> bool:
        return next(filter(lambda restaurant: restaurant.site == site, self.all_sites), None) is not None


def get_score(restaurant: CombinedRestaurant, all_restaurants: List[CombinedRestaurant]) -> float:
    total_score: float = 0.0
    for info in restaurant.all_sites:
        # Without Needed Context
        rating_score: float = max((info.average_rating() - 8),0) * 5
        popularity_score: float = min(info.number_of_reviews() / 10, 10)
        # Context Needed
        all_restaurants_from_type: List[Restaurant] = [restaurant.get_from_site(info.site) for restaurant in all_restaurants if restaurant.has_entry_on_site(info.site)]
        best_ranked_restaurant: Restaurant = min(all_restaurants_from_type, key=lambda restaurant: restaurant.rank())
        worst_ranked_restaurant: Restaurant = max(all_restaurants_from_type, key=lambda restaurant: restaurant.rank())
        relative_rank: float = (info.rank() - best_ranked_restaurant.rank()) / (worst_ranked_restaurant.rank() - best_ranked_restaurant.rank()) # Number between 0 and 1, 0 is the best ranked
        rank_score = (1 - relative_rank) * 10 # Now higher is better
        total_score += rating_score * 0.8 + popularity_score * 0.1 + rank_score * 0.1
    total_score = total_score / len(restaurant.all_sites)
    return total_score



def get_google_maps_restaurants(town: str, api_key: str, number_of_restaurants: int) -> List[Restaurant]:
    response: dict = get_google_maps_response(town, api_key)
    list_of_restaurants: List[dict] = response["results"]
    all_infos: List[Restaurant] = [gm.from_response(info, i) for i,info in enumerate(list_of_restaurants)]
    return all_infos


def get_google_maps_response(town: str, api_key: str) -> dict:
    if town == "nice france":
        file: Path = Path("nice_google_maps.json")
        cached_result: dict = json.load(file.open())
        return cached_result

    search_query: str = f"restaurants in {town}"
    url: str = f"https://maps.googleapis.com/maps/api/place/textsearch/json?key={api_key}&query={search_query}"
    response: dict = requests.get(url).json()
    return response


def get_tripadvisor_restaurants(town: str, api_key: str, number_of_restaurants: int) -> List[Restaurant]:
    # Get URL
    tripadvisor_url: str = get_tripadvisor_url(town, api_key)
    # Get Restaurants
    arguments: List = [(tripadvisor_url, min_rank) for min_rank in range(0,number_of_restaurants, 30)]
    with ThreadPool(len(arguments)) as pool:
        top_restaurants: List[Restaurant] = pool.starmap(get_restaurants_on_page, arguments)
    top_restaurants = flatten_list(top_restaurants)
    return top_restaurants


def get_tripadvisor_url(town: str, api_key: str) -> str:
    google_search_api_response: dict = get_tripadvisor_candidates(town, api_key)
    all_results: List[dict] = google_search_api_response["items"]
    general_restaurant_entry: dict = next(filter(lambda entry: "BEST Restaurants in".lower() in entry["title"].lower(), all_results))
    assert general_restaurant_entry is not None
    return general_restaurant_entry["link"]


def get_tripadvisor_candidates(town: str, api_key: str) -> dict:
    if town.lower() == "nice france":
        file: Path = Path("nice_google_search.json")
        cached_result: dict = json.load(file.open())
        return cached_result

    query: str = f"{town} restaurants"
    custom_engine: str = "014251365787875374948:lrj7gwbei0z"
    api_key: str = api_key
    api_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={custom_engine}&key={api_key}"
    return requests.get(api_url).json()


def get_restaurants_on_page(base_url: str, minimum_rank: int) -> List[Restaurant]:
    page_url: str = get_url_for_page(base_url, minimum_rank)
    html_file: str = requests.get(page_url).text
    soup: BeautifulSoup = BeautifulSoup(html_file, features="html.parser")
    all_top_restaurants: ResultSet = soup.find_all("div", {"class": "restaurants-list-ListCell__cellContainer--2mpJS"})
    infos: List[Restaurant] = [ta.from_tag(tag) for tag in all_top_restaurants]
    infos = [info for info in infos if not info.is_ad()]
    return infos


def get_url_for_page(base_url: str, minimum_rank: int) -> str:
    location_id: str = re.findall("-g[0-9]*", base_url)[0]
    split_by_location_id: List[str] = base_url.split(location_id)
    new_url: str = f"{split_by_location_id[0]}{location_id}-oa{minimum_rank}{split_by_location_id[1]}"
    return new_url


def flatten_list(multidimensional_list: List) -> List:
    return [item for items in multidimensional_list for item in items]


api_key: str = sys.argv[1]
town: str = "antibes"
tripadvisor: List[Restaurant] = get_tripadvisor_restaurants(town, api_key, 100)
google_maps: List[Restaurant] = get_google_maps_restaurants(town, api_key, 100)

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
    score: float = get_score(restaurant, combined_restaurants)
    print(f"name: {restaurant.all_sites[0].name()} size: {len(restaurant.all_sites)}, score: {score}")




