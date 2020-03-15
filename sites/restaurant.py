from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import List

from sites.rating_sites import SiteType


@dataclass
class RestaurantInformation:
    name: str
    link: str


@dataclass
class RestaurantRating:
    rating: float
    number_of_reviews: int
    rank: int


@dataclass
class Restaurant:
    info: RestaurantInformation
    rating: RestaurantRating
    site: SiteType


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
        return self.info.link

    def get_site(self) -> SiteType:
        return self.site


@dataclass
class CombinedRestaurant:
    all_sites: List[Restaurant]

    def get_from_site(self, site: SiteType) -> Restaurant:
        info_from_site: Restaurant = next(filter(lambda restaurant: restaurant.get_site() == site, self.all_sites), None)
        assert info_from_site is not None
        return info_from_site

    def has_entry_on_site(self, site: SiteType) -> bool:
        return next(filter(lambda restaurant: restaurant.get_site() == site, self.all_sites), None) is not None

    # noinspection PyUnresolvedReferences
    def get_score(self, all_restaurants: List[CombinedRestaurant]) -> float:
        total_score: float = 0.0
        for site_reviews in self.all_sites:
            # Without Needed Context
            rating_score: float = max((site_reviews.average_rating() - 8),0) * 5
            popularity_score: float = min(site_reviews.number_of_reviews() / 10, 10)
            total_score += rating_score * 0.9 + popularity_score * 0.1
        total_score = total_score / len(self.all_sites)
        return total_score

    def get_name(self) -> str:
        return self.get_from_site(SiteType.GOOGLE_MAPS).name()