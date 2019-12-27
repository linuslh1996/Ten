from dataclasses import dataclass
from enum import IntEnum


@dataclass
class RestaurantInformation:
    name: str
    link: str


@dataclass
class RestaurantRating:
    rating: float
    number_of_reviews: int
    rank: int


class RatingSite(IntEnum):
    GOOGLE_MAPS = 1,
    TRIP_ADVISOR = 2


class Restaurant:

    def __init__(self, info: RestaurantInformation, rating: RestaurantRating, site: RatingSite):
        self.info: RestaurantInformation = info
        self.rating: RestaurantRating = rating
        self.site: RatingSite = site

    def __str__(self) -> str:
        presentation: str = f"name: {self.name()} \n" \
                            f"url: {self.url()} \n" \
                            f"rating: {self.rating()} \n" \
                            f"number of reviews: {self.number_of_reviews()} \n" \
                            f"rank: {self.rank()}"
        return presentation

    def is_ad(self) -> bool:
        return self.rating.rank == -1

    def rank(self) -> int:
        return self.rating.rank

    def average_rating(self) -> float:
        return self.rating.rating

    def number_of_reviews(self) -> int:
        return self.rating.number_of_reviews

    def name(self) -> str:
        return self.info.name

    def url(self) -> str:
        return self.info.url

    def site(self) -> RatingSite:
        return self.site