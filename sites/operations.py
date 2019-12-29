from typing import List


def flatten_list(multidimensional_list: List) -> List:
    return [item for items in multidimensional_list for item in items]