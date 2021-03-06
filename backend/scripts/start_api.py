from dataclasses import dataclass
from typing import List, Tuple

import uvicorn
from fastapi import FastAPI
from psycopg2.sql import Composed
from starlette.middleware.cors import CORSMiddleware

import os

from ratings import sql
from ratings.database import PostgresDatabase, get_column_names
from ratings.restaurant import *

app = FastAPI()
DATABASE_URL: str = os.environ["DATABASE_URL"]
POSTGRES_DB: PostgresDatabase = PostgresDatabase(DATABASE_URL)

# Allow Connections From Frontend

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

@dataclass
class Result:
    name: str

@app.get("/restaurants")
def get_restaurants(town: str):
    # Get Info For All Restaurants Without Expensive Photo Loading Operation
    sql_to_get_names: Composed = sql.get_restaurants_without_photos(town)
    results: List[Tuple[GoogleMapsResult, TripAdvisorResult]] = POSTGRES_DB\
        .get(sql_to_get_names)\
        .convert_to_two_types(GoogleMapsResult, TripAdvisorResult, accept_error=True)
    google_maps_results: List[GoogleMapsResult] = [result[0] for result in results]
    trip_advisor_results: List[TripAdvisorResult] = [result[1] for result in results]
    assert (len(results)) != 0, "Could not load results"
    # Sort Restaurants To Get The 10 Best Restaurants
    sorted_by_score = sorted(results, key=lambda result: result[0].get_score(google_maps_results) + result[1].get_score(trip_advisor_results), reverse=True)
    # Complete Restaurant Data By Loading Photos Into It
    sql_to_get_all_info: Composed = sql.get_all_restaurant_info(tuple([result[0].link for result in sorted_by_score[:10]]))
    completed_results: List[Tuple[GoogleMapsResult, TripAdvisorResult]] = POSTGRES_DB\
        .get(sql_to_get_all_info)\
        .convert_to_two_types(GoogleMapsResult, TripAdvisorResult)
    return [{"google_maps_info": result[0], "trip_advisor_info":result[1]} for result in completed_results]


@app.get("/all_supported_towns")
def get_all_available_towns():
    sql_to_get_all_available_towns = sql.get_all_available_towns()
    list_of_towns: List[str] = POSTGRES_DB.get(sql_to_get_all_available_towns).convert_to_primitive_type(str)
    return list_of_towns

if __name__ == "__main__":
    names = get_column_names(CombinedRestaurant)
    uvicorn.run(app, port=5000)
