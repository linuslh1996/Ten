from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List

from dataclasses_json import dataclass_json


class SiteType(str, Enum):
    GOOGLE_MAPS = "google_maps",
    TRIP_ADVISOR = "trip_advisor"

@dataclass_json
@dataclass
class Restaurant:
    name: str
    link: str
    number_of_reviews: int
    rating: float
    site: SiteType

    def __str__(self) -> str:
        presentation: str = f"name: {self.name} \n" \
                            f"url: {self.link} \n" \
                            f"number of reviews: {self.number_of_reviews} \n"
        return presentation

    def __init__(self, *, name: str, link: str, rating: float, number_of_reviews: int, site: SiteType):
        self.name = name
        self.link = link
        self.number_of_reviews = number_of_reviews
        self.rating = rating
        self.site = site



@dataclass_json
@dataclass
class CombinedRestaurant:
    name: str
    all_sites: List[Restaurant]
    review: str
    score: float





