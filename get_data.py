from dataclasses import dataclass
from pathlib import Path
import json
from typing import List
import sys

import requests
import re
from bs4 import BeautifulSoup, ResultSet, Tag


@dataclass
class RestaurantInfo:
    name: str
    link: str
    rating: int
    number_of_reviews: int
    rank: int


    def __init__(self, restaurant_tag: Tag):
        self.name = self._get_name(restaurant_tag)
        self.link = self._get_link(restaurant_tag) # it is without tripadvisor in front of it
        self.rating = self._get_rating(restaurant_tag)
        self.number_of_reviews = self._get_number_of_reviews(restaurant_tag)
        self.rank = self._get_rank(restaurant_tag)

    def is_ad(self) -> bool:
        return self.rank == -1


    def _get_link(self, restaurant_tag: Tag) -> str:
        link: Tag = self._get_link_tag(restaurant_tag)
        url: str =  link.get("href")
        url = f"www.tripadvisor.com{url}"
        return url

    def _get_name(self, restaurant_tag: Tag) -> str:
        displayed_name: str = self._get_full_name(restaurant_tag)
        restaurant_name: str = displayed_name.split(". ")[-1]
        return restaurant_name

    def _get_rating(self, restaurant_tag: Tag) -> int:
        rating_tag: Tag = restaurant_tag.find_all("span", {"class": re.compile("ui_bubble")})[0]
        bubble_name: str = rating_tag.get("class")[1]
        rating: int = int(int(bubble_name.split("_")[-1]) * 2 / 10)
        return rating

    def _get_number_of_reviews(self, restaurant_tag: Tag) -> int:
        review_tag: Tag = restaurant_tag.find_all("span", {"class": re.compile("userReviewCount")})[0]
        review_name: str = review_tag.string
        return int(review_name.split(" ")[0])

    def _get_rank(self, restaurant_tag) -> int:
        displayed_name: str = self._get_full_name(restaurant_tag)
        rank: int
        try:
            rank = int(displayed_name.split(". ")[0])
        except ValueError:
            rank = -1
        return rank

    def _get_link_tag(self, restaurant_tag: Tag) -> Tag:
        return restaurant_tag.find_all("a")[0]

    def _get_full_name(self, restaurant_tag: Tag) -> str:
        test_tag: Tag = restaurant_tag.find_all("div", {"class", "restaurants-list-ListCell__nameBlock--1hL7F"})[0]
        displayed_name: str = self._get_link_tag(test_tag).string
        return displayed_name









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


def get_top_restaurants(url: str) -> List[RestaurantInfo]:
    html_file: str = open("antibes.html")
    soup: BeautifulSoup = BeautifulSoup(html_file, features="html.parser")
    all_top_restaurants: ResultSet = soup.find_all("div", {"class": "restaurants-list-ListCell__cellContainer--2mpJS"})
    infos: List[RestaurantInfo] = [RestaurantInfo(tag) for tag in all_top_restaurants]
    infos = [info for info in infos if not info.is_ad()]
    for info in infos:
        print(f"name: {info.name}")
        print(f"url: {info.link}")
        print(f"rating: {info.rating}")
        print(f"number of reviews: {info.number_of_reviews}")
        print(f"rank: {info.rank}")
        print("")
    return infos

api_key: str = sys.argv[1]
url: str = get_top_restaurants_url("antibes", api_key)
top_restaurants: List[RestaurantInfo] = get_top_restaurants(url)
