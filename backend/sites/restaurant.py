from __future__ import annotations

import abc
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, List
import math

from dataclasses_json import dataclass_json
from sqlalchemy import Column, ARRAY, String, Integer, Float
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


# Definitions


class SiteType(str, Enum):
    GOOGLE_MAPS = "google_maps",
    TRIP_ADVISOR = "trip_advisor"

@dataclass
class RestaurantResult:
    name: str
    link: str
    number_of_reviews: int
    rating: float

    @abc.abstractmethod
    def get_site_provider(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def get_score(self, other_restaurants: List[RestaurantResult]) -> float:
        raise NotImplementedError


# Model


Base = declarative_base()

class GoogleMapsResult(Base, RestaurantResult):
    __tablename__ = "google_maps"

    name = Column(String)
    link = Column(String, primary_key=True)
    number_of_reviews = Column(Integer)
    rating = Column(Float)
    formatted_address = Column(String)
    location_lang = Column(Float)
    location_lat = Column(Float)
    photos = Column(ARRAY(String))
    reviews = Column(ARRAY(String))

    def get_site_provider(self) -> str:
        return SiteType.GOOGLE_MAPS

    def get_score(self, other_restaurants: List[RestaurantResult]) -> float:
        return get_popularity_and_quality_weighted(self, other_restaurants)


class TripAdvisorResult(Base, RestaurantResult):
    __tablename__ = "trip_advisor"

    name = Column(String)
    link = Column(String, primary_key=True)
    number_of_reviews = Column(Integer)
    rating = Column(Float)

    def get_site_provider(self) -> str:
        return SiteType.TRIP_ADVISOR

    def get_score(self, other_restaurants: List[RestaurantResult]) -> float:
        return get_popularity_and_quality_weighted(self, other_restaurants)


class CombinedRestaurant(Base):
    __tablename__ = "restaurants"

    stadt = Column(String)
    trip_advisor_link = Column(String, primary_key=True)
    google_maps_link = Column(String, primary_key=True)


# Functions


def get_popularity_and_quality_weighted(restaurant: RestaurantResult, other_restaurants: List[RestaurantResult]) -> float:
    max_number_of_reviews: float = max([restaurant.number_of_reviews for restaurant in other_restaurants])
    popularity_score: float = math.log(restaurant.number_of_reviews, 2) / math.log(max_number_of_reviews, 2) * 10
    rating_score: float = (restaurant.rating - 7) * 10 / 3
    return math.sqrt(0.4 * popularity_score + 0.6 * rating_score)

def get_table_metadata() -> DeclarativeMeta:
    return Base

