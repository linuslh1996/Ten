import inspect
from typing import List, Dict, Any, Tuple, TypeVar, Type

import psycopg2
from psycopg2.extensions import cursor as Cursor
from psycopg2.extensions import connection as Connection

from psycopg2.sql import SQL, Identifier, Composable, Literal
from psycopg2.extras import execute_values
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import DeclarativeMeta


# Helper

T = TypeVar('T')

class DbEntry:

    def __init__(self, postgres_db, table_name: str, data: List[Dict]):
        self.postgres_db = postgres_db
        self.table_name: str = table_name
        self.data: List[Dict] = data

    def insert(self):
        self.postgres_db.insert(self.table_name, self.data)

    def upsert(self):
        self.postgres_db.upsert(self.table_name, self.data)

class DbResult:

    def __init__(self, data: List[Dict]):
        self.data = data

    def convert_rows_to(self, type: Type[T]) -> List[T]:
        # Get Info On Type
        empty_instance: T = _instanciate_new_instance(type)
        instance_variables: List[str] = _get_variables_of_type(empty_instance)
        # Recreate Type
        result: List[T] = []
        for entry in self.data:
            new_instance: T = _instanciate_new_instance(type)
            for variable in instance_variables:
                if not variable in entry.keys():
                    raise Exception(f"Could not find a value for {variable}")
                setattr(new_instance, variable, entry[variable])
            result.append(new_instance)
        return result


# Database


class PostgresDatabase:

    def __init__(self, database_url: str):
        self.connection: Connection = psycopg2.connect(database_url)
        self.cursor: Cursor = self.connection.cursor()

    def initialize_tables(self, database_url: str, base:DeclarativeMeta):
        engine = create_engine(database_url)
        base.metadata.create_all(engine)

    def get_table_names(self) -> List[str]:
        self.cursor.execute("""SELECT table_name FROM information_schema.tables
           WHERE table_schema = 'public'""")
        tables: List[str] = self.cursor.fetchall()
        return tables

    def get_column_names(self, table_name: str) -> List[str]:
        self.cursor.execute(SQL("SELECT * FROM {}").format(Identifier(table_name)))
        columnnames: List[str] = [desc[0] for desc in self.cursor.description]
        return columnnames

    def insert(self, table_name: str, data: List[Dict[str, Any]]):
        keys: List[str] = list(data[0].keys())
        as_identifiers: List[Identifier] = [Identifier(key) for key in keys]
        values = [list(entry.values()) for entry in data]
        execute_values(self.cursor, SQL("INSERT INTO {table_name} ({fields}) VALUES %s") \
                       .format(table_name=Identifier(table_name), fields=SQL(",").join(as_identifiers)),
                       values)
        self.connection.commit()

    def upsert(self, table_name: str, data: List[Dict]):
        primary_keys: List[str] = self._get_primary_keys(table_name)
        column_names: List[Identifier] = [Identifier(key) for key in data[0].keys()]
        all_values: List[List[Any]] = [list(entry.values()) for entry in data]
        for values in all_values:
            remaining_columns: List[Identifier] = [column_name for column_name in column_names if
                                                   not column_name.string in primary_keys]
            as_literals: List[Literal] = [Literal(value) for value in values]
            primary_keys_as_identifier = [Identifier(key) for key in primary_keys]
            a = "(" if len(remaining_columns) > 1 else ""
            b = ")" if len(remaining_columns) > 1 else ""
            sql: Composable = SQL("INSERT INTO {table_name} ({fields}) VALUES ({as_literals}) "
                                  "ON CONFLICT ({primary_keys}) "
                                  "DO UPDATE SET" + a + "{remaining_columns}" + b + " = " + a + "{remaining_values}" + b) \
                .format(table_name=Identifier(table_name), fields=SQL(",").join(column_names), as_literals=SQL(",").join(as_literals), primary_keys=SQL(",").join(primary_keys_as_identifier),
                        remaining_columns=SQL(",").join(remaining_columns), remaining_values=SQL("EXCLUDED.") + SQL(", EXCLUDED.").join(remaining_columns))
            self.cursor.execute(sql)
        self.connection.commit()

    def get(self, sql: Composable) -> DbResult:
        self.cursor.execute(sql)
        results_raw: List[Tuple] = self.cursor.fetchall()
        columnnames: List[str] = [desc[0] for desc in self.cursor.description]
        results: List[Dict] = []
        for result in results_raw:
            entry: Dict = dict(zip(columnnames, result))
            results.append(entry)
        return DbResult(results)

    def convert_to_db_entry(self, data: List[T], table_name: str) -> DbEntry:
        column_names: List[str] = self.get_column_names(table_name)
        db_entry: List[Dict] = []
        for entry in data:
            db_row: Dict = {}
            instance_variables: List[str] = _get_variables_of_type(entry)
            for column_name in column_names:
                if column_name not in instance_variables:
                    raise Exception(f"Could not map object to table {table_name}. Column {column_name} not found.")
                db_row[column_name] = getattr(entry, column_name)
            db_entry.append(db_row)
        return DbEntry(self, table_name, db_entry)

    def _get_primary_keys(self, table_name: str) -> List[str]:
        sql: Composable = SQL("SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type "
                              "FROM pg_index i JOIN  pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey) "
                              "WHERE  i.indrelid = {table_name}::regclass AND i.indisprimary") \
            .format(table_name=Literal(table_name))
        results: List[Dict] = self.get(sql).data
        return [result["attname"] for result in results]


def _instanciate_new_instance(type: Type[T]) -> T:
    constructor_arguments: List = list(inspect.signature(type.__init__).parameters.keys())
    arguments: Dict = {key: None for key in constructor_arguments if not key == "self"}
    try:
        empty_instance: T = type(**arguments)
    except TypeError:
        empty_instance = type()
    return empty_instance

def _get_variables_of_type(instance: T) -> List[str]:
    is_sql_alchemy_class: bool = hasattr(instance, "__tablename__")
    if is_sql_alchemy_class:
        variables = list(vars(instance.__class__).items())
    else:
        variables = list(vars(instance).items())
    without_protected = [key for key, value in variables if not key.startswith("_") and not isinstance(value, MetaData)
                         and not callable(value)]
    return without_protected