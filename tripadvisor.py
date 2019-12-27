import re

from bs4 import Tag

from restaurant import Restaurant, RestaurantRating, RestaurantInformation, RatingSite


def __str__(self) -> str:
    presentation: str = f"name: {self.name} \n" \
                        f"url: {self.link} \n" \
                        f"rating: {self.average_rating} \n" \
                        f"number of reviews: {self.number_of_reviews} \n" \
                        f"rank: {self.rank}"
    return presentation


def from_tag(restaurant_tag: Tag) -> Restaurant:
    name: str = _get_name(restaurant_tag)
    link: str = _get_link(restaurant_tag)  # it is without tripadvisor in front of it
    rating: float = _get_rating(restaurant_tag)
    number_of_reviews: int = _get_number_of_reviews(restaurant_tag)
    rank: int = _get_rank(restaurant_tag)
    return Restaurant(RestaurantInformation(name, link), RestaurantRating(rating, number_of_reviews, rank), RatingSite.TRIP_ADVISOR)


def _get_link(restaurant_tag: Tag) -> str:
    link: Tag = _get_link_tag(restaurant_tag)
    url: str =  link.get("href")
    url = f"www.tripadvisor.com{url}"
    return url


def _get_name(restaurant_tag: Tag) -> str:
    displayed_name: str = _get_full_name(restaurant_tag)
    restaurant_name: str = displayed_name.split(". ")[-1]
    return restaurant_name


def _get_rating(restaurant_tag: Tag) -> float:
    try:
        rating_tag: Tag = restaurant_tag.find_all("span", {"class": re.compile("ui_bubble")})[0]
        bubble_name: str = rating_tag.get("class")[1]
        rating: float = int(bubble_name.split("_")[-1]) * 2 / 10
    except IndexError:
        rating = -1
    return rating


def _get_number_of_reviews(restaurant_tag: Tag) -> int:
    try:
        review_tag: Tag = restaurant_tag.find_all("span", {"class": re.compile("userReviewCount")})[0]
        review_name: str = review_tag.string
        review_name = review_name.replace(",", "")
        number_of_reviews: int = int(review_name.split(" ")[0])
    except IndexError:
        number_of_reviews = -1
    return number_of_reviews


def _get_rank(restaurant_tag) -> int:
    displayed_name: str = _get_full_name(restaurant_tag)
    rank: int
    try:
        rank = int(displayed_name.split(". ")[0])
    except ValueError:
        rank = -1
    return rank


def _get_link_tag(restaurant_tag: Tag) -> Tag:
    return restaurant_tag.find_all("a")[0]


def _get_full_name(restaurant_tag: Tag) -> str:
    test_tag: Tag = restaurant_tag.find_all("div", {"class", "restaurants-list-ListCell__nameBlock--1hL7F"})[0]
    displayed_name: str = _get_link_tag(test_tag).string
    return displayed_name