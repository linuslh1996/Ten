from pathlib import Path
import json
from typing import List
import sys

import requests



def get_google_search_result(town: str, api_key: str) -> dict:
    if town.lower() == "antibes":
        file: Path = Path("antibes_google_response.json")
        cached_result: dict = json.load(file.open())
        return cached_result

    query: str = f"{town}+restaurants"
    custom_engine: str = "014251365787875374948:lrj7gwbei0z"
    api_key: str = api_key
    api_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={custom_engine}&key={api_key}"
    return requests.get(api_url).json()


def get_top_restaurants_url(town: str, api_key: str) -> str:
    google_search_api_response: dict = get_google_search_result(town, api_key)
    all_results: List[dict] = google_search_api_response["items"]
    general_restaurant_entry: dict = next(filter(lambda entry: "BEST Restaurants in".lower() in entry["title"].lower(), all_results))
    assert general_restaurant_entry is not None
    return general_restaurant_entry["link"]


def get_top_restaurants(url: str) -> dict:

api_key: str = sys.argv[1]
url: str = get_top_restaurants_url("antibes", api_key)