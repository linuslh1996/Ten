from typing import List, Optional

import difflib
from sites.restaurant import RestaurantResult
from textblob import TextBlob


def get_same_restaurant(restaurant: RestaurantResult, cached_results: List[RestaurantResult]) -> Optional[RestaurantResult]:
    name: str = get_formatted_name(restaurant.name)
    names: List[str] = [get_formatted_name(restaurant.name) for restaurant in cached_results]

    closest_matches: List[str] = difflib.get_close_matches(name, names, n=1, cutoff=0.75)
    if len(closest_matches) == 0:
        return None
    most_similar_restaurant = next(filter(lambda cur_restaurant: get_formatted_name(cur_restaurant.name) == closest_matches[0], cached_results), None)
    return most_similar_restaurant

def get_formatted_name(restaurant_name: str) -> str:
    to_lower: str = restaurant_name.lower()
    without_restaurant: str = to_lower.replace("restaurant", "")
    return without_restaurant


def flatten_list(multidimensional_list: List) -> List:
    return [item for items in multidimensional_list for item in items]


def choose_best_review(reviews: List[str]) -> str:
    ordered_by_length: List[str] = sorted(reviews, key=lambda review: len(review))
    return ordered_by_length[-1]


def _get_sentiment(review: str) -> float:
    blob: TextBlob = TextBlob(review)
    return abs(blob.polarity)