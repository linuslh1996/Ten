from restaurant import Restaurant, RestaurantInformation, RestaurantRating, RatingSite


def from_response(response: dict, rank: int) -> Restaurant:
    # Info
    name: str = response["name"]
    id: int = response["place_id"]
    url: str = f"https://www.google.com/maps/place/?q=place_id:{id}"
    info: RestaurantInformation = RestaurantInformation(name, url)
    # Rating
    rating: float = response["rating"] * 2
    number_of_reviews: int = response["user_ratings_total"]
    rating: RestaurantRating = RestaurantRating(rating, number_of_reviews, rank)
    return Restaurant(info, rating, RatingSite.GOOGLE_MAPS)



