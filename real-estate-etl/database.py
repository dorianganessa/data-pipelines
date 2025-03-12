import logging
import polars as pl
import duckdb


def create_properties_table(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        CREATE TABLE IF NOT EXISTS main.properties (
            url VARCHAR PRIMARY KEY,
            title VARCHAR,
            content VARCHAR[],    -- storing list[str] as an array of VARCHAR
            price BIGINT,
            city VARCHAR,
            neighbourhood VARCHAR,
            road VARCHAR,
            square_meters BIGINT,
            floor BIGINT,
            garage_info VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def get_new_properties(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
    new_rows_df = con.execute("""
        SELECT nd.*
        FROM new_data nd
        WHERE nd.url NOT IN (SELECT url FROM main.properties)
    """).pl()
    return new_rows_df


def insert_new_properties(con: duckdb.DuckDBPyConnection) -> None:
    con.execute("""
        INSERT INTO properties (url, title, content, price, city, neighbourhood, road, square_meters, floor, garage_info)
        SELECT nd.url, nd.title, nd.content, nd.price, nd.city, nd.neighbourhood, nd.road, nd.square_meters, nd.floor, nd.garage_info
        FROM new_data nd
        WHERE nd.url NOT IN (SELECT url FROM main.properties)
    """)