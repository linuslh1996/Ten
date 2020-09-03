from dataclasses import dataclass
from typing import List

import uvicorn
from fastapi import FastAPI
from psycopg2.sql import Composed
from starlette.middleware.cors import CORSMiddleware

import os

from sites import sql
from sites.database import PostgresDatabase, get_column_names
from sites.restaurant import *

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
    sql_to_get_names: Composed = sql.get_restaurants_without_photos(town)
    results = POSTGRES_DB.get(sql_to_get_names).convert_to_two_types(GoogleMapsResult, TripAdvisorResult, accept_error=True)
    google_maps_results = [result[0] for result in results]
    trip_advisor_results = [result[1] for result in results]
    sorted_by_score = sorted(results, key=lambda result: result[0].get_score(google_maps_results) + result[1].get_score(trip_advisor_results), reverse=True)
    sql_to_get_all_info: Composed = sql.get_all_restaurant_info(tuple([result[0].link for result in sorted_by_score[:10]]))
    results = POSTGRES_DB.get(sql_to_get_all_info).convert_to_two_types(GoogleMapsResult, TripAdvisorResult)
    return [{"google_maps_info": result[0], "trip_advisor_info":result[1]} for result in results]



if __name__ == "__main__":
    names = get_column_names(CombinedRestaurant)
    uvicorn.run(app, port=5000)
