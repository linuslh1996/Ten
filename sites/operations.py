from typing import List, Optional

import numpy as np
import difflib
from sites.restaurant import Restaurant


def flatten_list(multidimensional_list: List) -> List:
    return [item for items in multidimensional_list for item in items]


def get_same_restaurant(restaurant: Restaurant, cached_results: List[Restaurant]) -> Optional[Restaurant]:
    name: str = restaurant.name().lower()
    names: str = [restaurant.name().lower() for restaurant in cached_results]
    closest_matches: List[str] = difflib.get_close_matches(name, names, n=1, cutoff=0.75)
    if len(closest_matches) == 0:
        return None
    most_similar_restaurant = next(filter(lambda cur_restaurant: cur_restaurant.name().lower() == closest_matches[0], cached_results))
    return most_similar_restaurant