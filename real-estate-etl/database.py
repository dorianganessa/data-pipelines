import logging
import polars as pl
import duckdb


def create_properties_table(con: duckdb.DuckDBPyConnection) -> None:
        # Create the table 'properties'
    con.execute("""
        CREATE TABLE IF NOT EXISTS main.properties (
            url VARCHAR PRIMARY KEY,
            title VARCHAR,
            content VARCHAR[],    -- storing list[str] as an array of VARCHAR
            price BIGINT,
            road VARCHAR,
            square_meters BIGINT,
            floor BIGINT,
            garage_info VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


def get_new_properties(con: duckdb.DuckDBPyConnection) -> pl.DataFrame:
        # Use a LEFT JOIN to filter out rows that already exist in 'properties'
    new_rows_df = con.execute("""
        SELECT nd.*
        FROM new_data nd
        LEFT JOIN main.properties p ON nd.url = p.url
        WHERE p.url IS NULL
    """).pl()


def insert_new_properties(con: duckdb.DuckDBPyConnection) -> None:
        # Insert the new rows into the 'properties' table
    con.execute("""
        INSERT INTO properties
        SELECT nd.*
        FROM new_data nd
        LEFT JOIN main.properties p ON nd.url = p.url
        WHERE p.url IS NULL
    """)