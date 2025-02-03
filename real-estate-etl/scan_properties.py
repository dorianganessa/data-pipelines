from bs4 import BeautifulSoup
import polars as pl
import duckdb
from scraper import parse_listing
from database import create_properties_table, get_new_properties, insert_new_properties
from dotenv import load_dotenv
import os
from telegram_api import send_message, format_property_message



if __name__ == "__main__":


    load_dotenv()

    url: str = os.getenv("scrape_url")
    warehouse_name: str = os.getenv("warehouse_name")
    motherduck_token: str = os.getenv("motherduck_token")

    data: list[dict] = parse_listing(url)
    polars_df: pl.DataFrame = pl.DataFrame(data)

    con: duckdb.DuckDBPyConnection = duckdb.connect(f"md:{warehouse_name}?motherduck_token={motherduck_token}")

    create_properties_table(con)
    
    con.register("new_data", polars_df)

    new_rows_df: pl.DataFrame = get_new_properties(con)


    insert_new_properties(con)

    # Iterate over the DataFrame and format each property
    if new_rows_df is not None and not new_rows_df.is_empty():
        messages: list[str] = [format_property_message(row) for row in new_rows_df.iter_rows(named=True)]
    else:
        messages = []

# Send messages in chunks of two
    for i in range(0, len(messages), 2):
        # Get the current chunk of two messages
        message_chunk: list[str] = messages[i:i+2]
        # Join the two messages with a separator
        full_message: str = "\n\n".join(message_chunk)
        # Send the combined message
        send_message(full_message)


