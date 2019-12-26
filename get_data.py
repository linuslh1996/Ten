from dataclasses import dataclass
from pathlib import Path
import json
from typing import List
import sys

import requests
import re
from bs4 import BeautifulSoup, ResultSet, Tag
from multiprocessing.dummy import Pool as ThreadPool


@dataclass
class TripAdvisorRestaurant:
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

    def __str__(self) -> str:
        presentation: str = f"name: {self.name} \n" \
        f"url: {self.link} \n" \
        f"rating: {self.rating} \n" \
        f"number of reviews: {self.number_of_reviews} \n " \
        f"rank: {self.rank}"
        return presentation


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
        try:
            rating_tag: Tag = restaurant_tag.find_all("span", {"class": re.compile("ui_bubble")})[0]
            bubble_name: str = rating_tag.get("class")[1]
            rating: int = int(int(bubble_name.split("_")[-1]) * 2 / 10)
        except IndexError:
            rating = -1
        return rating

    def _get_number_of_reviews(self, restaurant_tag: Tag) -> int:
        try:
            review_tag: Tag = restaurant_tag.find_all("span", {"class": re.compile("userReviewCount")})[0]
            review_name: str = review_tag.string
            review_name = review_name.replace(",", "")
            number_of_reviews: int = int(review_name.split(" ")[0])
        except IndexError:
            number_of_reviews = -1
        return number_of_reviews

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



@dataclass
class GoogleMapsRestaurant:
    name: str

    def __init__(self, restaurant_info: dict):
        self.name = restaurant_info["name"]


def get_google_maps_restaurants(town: str, api_key: str, number_of_restaurants: int) -> List[GoogleMapsRestaurant]:
    search_query: str = f"restaurants in {town}"
    url: str = f"https://maps.googleapis.com/maps/api/place/textsearch/json?key={api_key}&query={search_query}"
    response: dict = requests.get(url).json()
    list_of_restaurants: List[dict] = response["results"]
    all_infos: List[GoogleMapsRestaurant] = [GoogleMapsRestaurant(info) for info in list_of_restaurants]
    print(all_infos)
    return all_infos


def get_tripadvisor_restaurants(town: str, api_key: str, number_of_restaurants: int) -> List[TripAdvisorRestaurant]:
    # Get URL
    tripadvisor_url: str = get_tripadvisor_url(town, api_key)
    # Get Restaurants
    arguments: List = [(tripadvisor_url, min_rank) for min_rank in range(0,number_of_restaurants, 30)]
    with ThreadPool(5) as pool:
        top_restaurants: list = pool.starmap(get_restaurants_on_page, arguments)
    top_restaurants = flatten_list(top_restaurants)
    for info in top_restaurants:
        print(info)
        print("")
    return top_restaurants


def get_tripadvisor_url(town: str, api_key: str) -> str:
    google_search_api_response: dict = search_tripadvisor_page(town, api_key)
    all_results: List[dict] = google_search_api_response["items"]
    general_restaurant_entry: dict = next(filter(lambda entry: "BEST Restaurants in".lower() in entry["title"].lower(), all_results))
    assert general_restaurant_entry is not None
    return general_restaurant_entry["link"]


def search_tripadvisor_page(town: str, api_key: str) -> dict:
    if town.lower() == "antibes":
        file: Path = Path("antibes_google_response.json")
        cached_result: dict = json.load(file.open())
        return cached_result

    query: str = f"{town} restaurants"
    custom_engine: str = "014251365787875374948:lrj7gwbei0z"
    api_key: str = api_key
    api_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={custom_engine}&key={api_key}"
    return requests.get(api_url).json()


def get_restaurants_on_page(base_url: str, minimum_rank: int) -> List[TripAdvisorRestaurant]:
    page_url: str = get_url_for_page(base_url, minimum_rank)
    html_file: str = requests.get(page_url).text
    soup: BeautifulSoup = BeautifulSoup(html_file, features="html.parser")
    all_top_restaurants: ResultSet = soup.find_all("div", {"class": "restaurants-list-ListCell__cellContainer--2mpJS"})
    infos: List[TripAdvisorRestaurant] = [TripAdvisorRestaurant(tag) for tag in all_top_restaurants]
    infos = [info for info in infos if not info.is_ad()]
    return infos


def get_url_for_page(base_url: str, minimum_rank: int) -> str:
    location_id: str = re.findall("-g[0-9]*", base_url)[0]
    split_by_location_id: List[str] = base_url.split(location_id)
    new_url: str = f"{split_by_location_id[0]}{location_id}-oa{minimum_rank}{split_by_location_id[1]}"
    return new_url


def flatten_list(multidimensional_list: List) -> List:
    return [item for items in multidimensional_list for item in items]


api_key: str = sys.argv[1]
town: str = "antibes"
google_maps = get_tripadvisor_restaurants(town, api_key, 400)
