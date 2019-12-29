import json
from pathlib import Path
from typing import List, Optional

import requests
import time

import sites.operations as op
from sites.restaurant import Restaurant, RestaurantInformation, RestaurantRating, RatingSite


def get_restaurants(town: str, api_key: str, number_of_restaurants: int) -> List[Restaurant]:
    responses: List[dict] = _get_google_maps_response(town, api_key)
    list_of_restaurants: List[Restaurant] = [response["results"] for response in responses]
    flattened_list = op.flatten_list(list_of_restaurants)
    all_infos: List[Restaurant] = [from_response(info, i) for i,info in enumerate(flattened_list)]
    return all_infos

def get_same_restaurant(restaurant: Restaurant, cached_results: List[Restaurant]) -> Optional[Restaurant]:
    assert(all([restaurant.get_site() == RatingSite.GOOGLE_MAPS for restaurant in cached_results]))
    return op.get_same_restaurant(restaurant, cached_results)


def from_response(response: dict, rank: int) -> Restaurant:
    # Info
    name: str = response["name"]
    id: int = response["place_id"]
    url: str = f"https://www.google.com/maps/place/?q=place_id:{id}"
    info: RestaurantInformation = RestaurantInformation(name, url)
    # Rating
    rating: float = response["rating"] * 2
    number_of_reviews: int = response["user_ratings_total"]
    rating: RestaurantRating = RestaurantRating(rating, number_of_reviews, rank)
    return Restaurant(info, rating, RatingSite.GOOGLE_MAPS)


def _get_google_maps_response(town: str, api_key: str) -> List[dict]:
    # Cached
    if town == "nice france":
        file: Path = Path("nice_google_maps.json")
        cached_result: dict = json.load(file.open())
        return [cached_result]
    # Generate Normally
    search_query: str = f"restaurants in {town}"
    url: str = f"https://maps.googleapis.com/maps/api/place/textsearch/json?key={api_key}&query={search_query}"
    all_responses: List[dict] = []
    response: dict = requests.get(url).json()
    all_responses.append(response.copy())
    # Multiple Pages
    for i in range(2):
        response = _get_next_result(response, api_key)
        all_responses.append(response.copy())
    return all_responses


def _get_next_result(response: dict, api_key: str) -> dict:
    pagetoken: str = response["next_page_token"]
    time.sleep(1.5)
    next_page: dict = requests.get(f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={pagetoken}&key={api_key}").json()
    return next_page



