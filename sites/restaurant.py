from dataclasses import dataclass
from enum import IntEnum
from typing import List


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