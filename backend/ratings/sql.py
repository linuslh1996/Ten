from typing import Tuple, Dict, List

from psycopg2.sql import SQL, Literal, Composed, Identifier
from sqlalchemy.ext.declarative import DeclarativeMeta

from ratings.restaurant import *
from ratings.database import get_column_names, DbResult


def get_aliased_select(table: DeclarativeMeta, table_shortcut: str=None, columns: List[str] = None) -> SQL:
    if table_shortcut is None:
        # noinspection PyUnresolvedReferences
        table_shortcut = table.__tablename__
    if columns is None:
        columns = get_column_names(table)
    aliases: List[str] = []
    for column in columns:
        # noinspection PyUnresolvedReferences
        aliases.append(f"{table_shortcut}.{column} as {DbResult.get_column_alias(table.__tablename__, column)}")
    return SQL(", ".join(aliases)) + SQL(" ")


def get_restaurants_without_photos(town: str) -> Composed:
    columns = [column for column in get_column_names(GoogleMapsResult) if not column == "photos"]
    fields_to_select = get_aliased_select(GoogleMapsResult, columns=columns) + SQL(", ") + get_aliased_select(TripAdvisorResult)
    sql = SQL("SELECT {fields_to_select} FROM restaurants "
                "INNER JOIN google_maps ON google_maps.link = restaurants.google_maps_link "
                "INNER JOIN trip_advisor ON restaurants.trip_advisor_link  = trip_advisor.link "
              "WHERE town = {town}")
    return sql.format(town=Literal(town), fields_to_select=fields_to_select)


def get_all_restaurant_info(google_maps_links: Tuple) -> Composed:
    columns = [column for column in get_column_names(GoogleMapsResult) if not column == "photos"]
    fields_to_select: SQL = get_aliased_select(GoogleMapsResult, columns=columns) + SQL(", array[encode(photos[1]::bytea,'escape'), encode(photos[2]::bytea,'escape'), encode(photos[3]::bytea,'escape')] as google_maps_photos, ") + get_aliased_select(TripAdvisorResult)
    sql = SQL("SELECT {fields_to_select} FROM restaurants "
              "INNER JOIN google_maps ON google_maps.link = restaurants.google_maps_link "
              "INNER JOIN trip_advisor ON restaurants.trip_advisor_link  = trip_advisor.link "
              "WHERE restaurants.google_maps_link IN {google_maps_links}")
    return sql.format(fields_to_select=fields_to_select, google_maps_links=Literal(google_maps_links))

def get_all_available_towns() -> SQL:
    sql = SQL("SELECT DISTINCT town FROM restaurants")
    return sql