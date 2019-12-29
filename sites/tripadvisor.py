import json
import re
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import List

import requests
from bs4 import Tag, BeautifulSoup, ResultSet

from sites.operations import flatten_list
from sites.restaurant import Restaurant, RestaurantRating, RestaurantInformation, RatingSite


def get_restaurants(town: str, api_key: str, number_of_restaurants: int) -> List[Restaurant]:
    # Get URL
    tripadvisor_url: str = _get_tripadvisor_page(town, api_key)
    # Get Restaurants
    arguments: List = [_get_url_for_page(tripadvisor_url, min_rank) for min_rank in range(0,number_of_restaurants, 30)]
    with ThreadPoolExecutor(max_workers=10) as pool:
        top_restaurants: List[Restaurant] = pool.map(_get_restaurants_on_page, arguments)
    top_restaurants = flatten_list(top_restaurants)
    return top_restaurants


def from_tag(restaurant_tag: Tag) -> Restaurant:
    name: str = _get_name(restaurant_tag)
    link: str = _get_link(restaurant_tag)  # it is without tripadvisor in front of it
    rating: float = _get_rating(restaurant_tag)
    number_of_reviews: int = _get_number_of_reviews(restaurant_tag)
    rank: int = _get_rank(restaurant_tag)
    return Restaurant(RestaurantInformation(name, link), RestaurantRating(rating, number_of_reviews, rank), RatingSite.TRIP_ADVISOR)


# Collecting Restaurants

def _get_tripadvisor_page(town: str, api_key: str) -> str:
    google_search_api_response: dict = _get_tripadvisor_candidates(town, api_key)
    all_results: List[dict] = google_search_api_response["items"]
    general_restaurant_entry: dict = next(filter(lambda entry: "BEST Restaurants in".lower() in entry["title"].lower(), all_results))
    assert general_restaurant_entry is not None
    return general_restaurant_entry["link"]


def _get_url_for_page(base_url: str, minimum_rank: int) -> str:
    location_id: str = re.findall("-g[0-9]*", base_url)[0]
    split_by_location_id: List[str] = base_url.split(location_id)
    new_url: str = f"{split_by_location_id[0]}{location_id}-oa{minimum_rank}{split_by_location_id[1]}"
    return new_url


def _get_restaurants_on_page(page_url: str) -> List[Restaurant]:
    html_file: str = requests.get(page_url).text
    soup: BeautifulSoup = BeautifulSoup(html_file, features="html.parser")
    all_top_restaurants: ResultSet = soup.find_all("div", {"class": "restaurants-list-ListCell__cellContainer--2mpJS"})
    infos: List[Restaurant] = [from_tag(tag) for tag in all_top_restaurants]
    infos = [info for info in infos if not info.is_ad()]
    return infos


def _get_tripadvisor_candidates(town: str, api_key: str) -> dict:
    if town.lower() == "nice france":
        file: Path = Path("nice_google_search.json")
        cached_result: dict = json.load(file.open())
        return cached_result

    query: str = f"{town} restaurants"
    custom_engine: str = "011204893081168402867:xebeg1mi0om"
    api_key: str = api_key
    api_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={custom_engine}&key={api_key}"
    return requests.get(api_url).json()

# Constructing From HTML

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










