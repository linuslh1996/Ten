import abc
import json
from concurrent.futures.thread import ThreadPoolExecutor
from enum import IntEnum
from pathlib import Path
from typing import List, Optional, Dict

import re
import requests
import time

from bs4 import Tag, NavigableString, BeautifulSoup, ResultSet

import sites.utils as op
from sites.restaurant import Restaurant, RestaurantInformation, RestaurantRating



class SiteType(IntEnum):
    GOOGLE_MAPS = 1,
    TRIP_ADVISOR = 2


class RatingSite:

    @abc.abstractmethod
    def get_restaurants(self, town: str, number_of_restaurants: int) -> List[Restaurant]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_same_restaurant(self, restaurant: Restaurant, cached_results: List[Restaurant], town: str) -> Optional[Restaurant]:
        raise NotImplementedError()

    @abc.abstractmethod
    def get_site_type(self) -> SiteType:
        raise NotImplementedError()



class GoogleMaps(RatingSite):

    def __init__(self, api_key: str):
        self._api_key: str = api_key

    # Public Methods

    def get_restaurants(self, town: str, number_of_restaurants: int) -> List[Restaurant]:
        responses: List[dict] = self._get_google_maps_response(town, self._api_key)
        list_of_restaurants: List[Restaurant] = [response["results"] for response in responses]
        flattened_list = op.flatten_list(list_of_restaurants)
        all_infos: List[Restaurant] = [self._from_response(info, i) for i, info in enumerate(flattened_list)]
        return all_infos

    def get_same_restaurant(self, restaurant: Restaurant, cached_results: List[Restaurant], town: str) -> Optional[Restaurant]:
        # See If We Already Found Restaurant
        assert(all([restaurant.get_site() == SiteType.GOOGLE_MAPS for restaurant in cached_results]))
        same_restaurant: Optional[Restaurant] = op.get_same_restaurant(restaurant, cached_results)
        if same_restaurant:
            return same_restaurant
        # Search With Google API
        url: str = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=restaurant {restaurant.name()} {town}&inputtype=textquery&fields=rating,user_ratings_total,name,place_id&key={self._api_key}"
        response: dict = requests.get(url).json()
        try:
            candidate: dict = response["candidates"][0]
            return self._from_response(candidate, -1)
        except IndexError:
            print(response)
            return None

    def get_site_type(self) -> SiteType:
        return SiteType.GOOGLE_MAPS


    def get_reviews(self, restaurant: Restaurant) -> List[str]:
        id: str = restaurant.url().split(":")[-1]
        url: str = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={id}&fields=review&key={self._api_key}"
        response: dict = requests.get(url).json()
        time.sleep(1)
        reviews: List[str] = [review["text"] for review in response["result"]["reviews"]]
        return reviews

    # Private Methods

    def _from_response(self, response: dict, rank: int) -> Restaurant:
        # Info
        name: str = response["name"]
        id: int = response["place_id"]
        url: str = f"https://www.google.com/maps/place/?q=place_id:{id}"
        info: RestaurantInformation = RestaurantInformation(name, url)
        # Rating
        rating: float = response["rating"] * 2
        number_of_reviews: int = response["user_ratings_total"]
        rating: RestaurantRating = RestaurantRating(rating, number_of_reviews, rank)
        return Restaurant(info, rating, SiteType.GOOGLE_MAPS)


    def _get_google_maps_response(self, town: str, api_key: str) -> List[dict]:
        # Cached
        if town == "nice france":
            file: Path = Path("nice_google_maps.json")
            cached_result: dict = json.load(file.open())
            return [cached_result]
        # Generate Normally
        search_query: str = f"restaurants in {town}"
        url: str = f"https://maps.googleapis.com/maps/api/place/textsearch/json?key={api_key}&query={search_query}"
        all_responses: List[dict] = []
        response: dict = requests.get(url).json()
        all_responses.append(response.copy())
        # Multiple Pages
        for i in range(2):
            response = self._get_next_result(response, api_key)
            all_responses.append(response.copy())
        return all_responses


    def _get_next_result(self, response: dict, api_key: str) -> dict:
        pagetoken: str = response["next_page_token"]
        time.sleep(2)
        next_page: dict = requests.get(f"https://maps.googleapis.com/maps/api/place/textsearch/json?pagetoken={pagetoken}&key={api_key}").json()
        return next_page



class TripAdvisor(RatingSite):



    def __init__(self, google_api_key: str):
        self._google_api_key: str = google_api_key


    # Public Methods

    def get_site_type(self) -> SiteType:
        return SiteType.TRIP_ADVISOR

    def get_restaurants(self, town: str, number_of_restaurants: int) -> List[Restaurant]:
        # Get URL
        tripadvisor_url: str = self._get_town_first_page(town, self._google_api_key)
        # Get Restaurants
        arguments: List = [self._get_url_for_ith_page(tripadvisor_url, min_rank) for min_rank in
                           range(0, number_of_restaurants, 30)]
        with ThreadPoolExecutor(max_workers=10) as pool:
            top_restaurants: List[Restaurant] = pool.map(self._get_restaurants_on_page, arguments)
        top_restaurants = op.flatten_list(top_restaurants)
        return top_restaurants


    def get_same_restaurant(self, restaurant: Restaurant, cached_results: List[Restaurant], town: str) -> Optional[Restaurant]:
        restaurants_are_tripadvisor = [restaurant.get_site() == SiteType.TRIP_ADVISOR for restaurant in
                                       cached_results]
        assert (all(restaurants_are_tripadvisor))
        return op.get_same_restaurant(restaurant, cached_results)


    # Collecting Restaurants

    def _get_town_first_page(self, town: str, api_key: str) -> str:
        google_search_for_town: dict
        if town.lower() == "nice france":
            file: Path = Path("nice_google_search.json")
            google_search_for_town = json.load(file.open())
        else:
            query: str = f"{town} restaurants"
            custom_engine: str = "011204893081168402867:xebeg1mi0om"
            api_key: str = api_key
            api_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={custom_engine}&key={api_key}"
            google_search_for_town = requests.get(api_url).json()
        all_results: List[dict] = google_search_for_town["items"]
        general_restaurant_entry: dict = next(
            filter(lambda entry: "BEST Restaurants in".lower() in entry["title"].lower(), all_results))
        assert general_restaurant_entry is not None
        return general_restaurant_entry["link"]

    def _get_url_for_ith_page(self, base_url: str, minimum_rank: int) -> str:
        location_id: str = re.findall("-g[0-9]*", base_url)[0]
        split_by_location_id: List[str] = base_url.split(location_id)
        new_url: str = f"{split_by_location_id[0]}{location_id}-oa{minimum_rank}{split_by_location_id[1]}"
        return new_url

    def _get_restaurants_on_page(self, page_url: str) -> List[Restaurant]:
        html_file: str = requests.get(page_url).text
        soup: BeautifulSoup = BeautifulSoup(html_file, features="html.parser")
        all_scripts: ResultSet = soup.find_all("scripts")
        # Extract Information
        info_text: NavigableString = all_scripts[0].string
        relevant_start: str = '"data":{"restaurants"'
        relevant_end: str = '}]},"error":null}'
        first_pos: int = info_text.find(relevant_start)
        last_pos: int = info_text.find(relevant_end) + len(relevant_end)
        data: Dict = json.loads(info_text[first_pos:last_pos])
        # Load Into Objects
        infos: List[Restaurant] = [self._from_tag(tag) for tag in all_scripts]
        infos = [info for info in infos if not info.is_ad()]
        return infos

    # Constructing From HTML

    def _from_tag(self, restaurant_tag: Tag) -> Restaurant:
        name: str = self._get_name(restaurant_tag)
        link: str = self._get_link(restaurant_tag)
        rating: float = self._get_rating(restaurant_tag)
        number_of_reviews: int = self._get_number_of_reviews(restaurant_tag)
        rank: int = self._get_rank(restaurant_tag)
        return Restaurant(RestaurantInformation(name, link), RestaurantRating(rating, number_of_reviews, rank),
                          SiteType.TRIP_ADVISOR)

    def _get_link(self, restaurant_tag: Tag) -> str:
        link: Tag = self._get_link_tag(restaurant_tag)
        url: str = link.get("href")
        url = f"www.tripadvisor.com{url}"
        return url

    def _get_name(self, restaurant_tag: Tag) -> str:
        displayed_name: str = self._get_full_name(restaurant_tag)
        restaurant_name: str = displayed_name.split(". ")[-1]
        return restaurant_name

    def _get_rating(self, restaurant_tag: Tag) -> float:
        try:
            rating_tag: Tag = restaurant_tag.find_all("span", {"class": re.compile("ui_bubble")})[0]
            bubble_name: str = rating_tag.get("class")[1]
            rating: float = int(bubble_name.split("_")[-1]) * 2 / 10
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



