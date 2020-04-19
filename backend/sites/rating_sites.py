import abc
import json
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Dict

import re
import requests
import time
import logging
from base64 import b64encode


from bs4 import BeautifulSoup, ResultSet

import sites.utils as op
from sites.restaurant import Restaurant, SiteType


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
        responses: List[Dict] = self._get_google_maps_response(town, self._api_key)
        list_of_restaurants: List[Dict] = [response["results"] for response in responses]
        flattened_list = op.flatten_list(list_of_restaurants)
        all_infos: List[Restaurant] = [self._from_response(info, i) for i, info in enumerate(flattened_list)]
        return all_infos

    def get_same_restaurant(self, restaurant: Restaurant, cached_results: List[Restaurant], town: str) -> Optional[Restaurant]:
        # See If We Already Found Restaurant
        assert(all([restaurant.site == SiteType.GOOGLE_MAPS for restaurant in cached_results]))
        same_restaurant: Optional[Restaurant] = op.get_same_restaurant(restaurant, cached_results)
        if same_restaurant:
            return same_restaurant
        search_string = f"{restaurant.name} {town}" if "restaurant" in restaurant.name.lower() else f"restaurant {restaurant.name} {town}"
        # Search With Google API
        url: str = f"https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={search_string}" \
                   f"&inputtype=textquery&fields=rating,user_ratings_total,name,place_id&key={self._api_key}"
        response: dict = requests.get(url).json()
        try:
            candidate: dict = response["candidates"][0]
            return self._from_response(candidate, -1)
        except IndexError:
            logging.exception(response)
            return None

    def get_site_type(self) -> SiteType:
        return SiteType.GOOGLE_MAPS


    def get_reviews(self, restaurant: Restaurant) -> List[str]:
        id: str = restaurant.link.split(":")[-1]
        url: str = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={id}&fields=review&key={self._api_key}"
        response: dict = requests.get(url).json()
        reviews: List[str] = [review["text"] for review in response["result"]["reviews"]]
        return reviews

    def get_images(self, restaurant: Restaurant) -> List[str]:
        id: str = restaurant.link.split(":")[-1]
        url: str = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={id}&fields=photos&key={self._api_key}"
        photo_references: List[str] = [photo["photo_reference"] for photo in requests.get(url).json()["result"]["photos"]]
        get_photo_url: str = f"https://maps.googleapis.com/maps/api/place/photo?maxheight=1500&photoreference={photo_references[0]}&key={self._api_key}"
        result = requests.get(get_photo_url)
        first_image: str = result.content
        base_64_encoded: str = b64encode(first_image)
        return [base_64_encoded]

    # Private Methods

    def _from_response(self, response: dict, rank: int) -> Restaurant:
        # Info
        name: str = response["name"]
        id: int = response["place_id"]
        url: str = f"https://www.google.com/maps/place/?q=place_id:{id}"
        # Rating
        rating: float = response["rating"] * 2
        number_of_reviews: int = response["user_ratings_total"]
        return Restaurant(site=SiteType.GOOGLE_MAPS, name=name, rating=rating, number_of_reviews=number_of_reviews, link=url)


    def _get_google_maps_response(self, town: str, api_key: str) -> List[dict]:
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
            top_restaurants: List[List[Restaurant]] = list(pool.map(self._get_restaurants_on_page, arguments))
        top_restaurants: List[Restaurant] = op.flatten_list(top_restaurants)
        return top_restaurants


    def get_same_restaurant(self, restaurant: Restaurant, cached_results: List[Restaurant], town: str) -> Optional[Restaurant]:
        restaurants_are_tripadvisor = [restaurant.site == SiteType.TRIP_ADVISOR for restaurant in
                                       cached_results]
        assert all(restaurants_are_tripadvisor)
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
        all_scripts: ResultSet = soup.find_all("script")
        # Get Fitting Script
        script_data: str
        for script in all_scripts:
            if not script.string:
                continue
            if "userReviewCount" in script.string:
                script_data = script.string
        # Extract Information
        relevant_start: str = '{"restaurants"'
        relevant_end: str = '}]},"error":null}'
        last_bracket_position: int = 3 # We want the string to end before the "error" tag starts.
        first_pos: int = script_data.find(relevant_start)
        last_pos: int = script_data.find(relevant_end) + last_bracket_position
        data: Dict = json.loads(script_data[first_pos:last_pos])
        # Load Into Objects
        infos: List[Restaurant] = [self._from_dict(restaurant) for restaurant in data["restaurants"]]
        return infos

    # Constructing From Json

    def _from_dict(self, restaurant: Dict) -> Restaurant:
        page_url: str = f'https://www.tripadvisor.com{restaurant["detailPageUrl"]}'
        name: str = restaurant["name"]
        average_rating: float = restaurant["averageRating"] * 2
        number_of_reviews = restaurant["userReviewCount"]
        return Restaurant(name=name, rating=average_rating, number_of_reviews=number_of_reviews,
                          link=page_url, site=SiteType.TRIP_ADVISOR)


