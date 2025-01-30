from typing import List, Dict, Any
from bs4 import BeautifulSoup
import polars as pl
import duckdb
from scraper import parse_listing
from database import clean_properties, get_new_properties
from dotenv import load_dotenv
import os
from telegram_api import send_message, format_property_message

def main() -> None:
    """Main function to scrape properties and send messages."""
    load_dotenv()

    url: str = os.getenv("scrape_url")
    warehouse_name: str = os.getenv("warehouse_name")
    motherduck_token: str = os.getenv("motherduck_token")

    if not url or not warehouse_name or not motherduck_token:
        raise ValueError("Environment variables for URL, warehouse name, or token are not set.")

    data: List[Dict[str, Any]] = parse_listing(url)

    polars_df: pl.DataFrame = pl.DataFrame(data)

    con: duckdb.DuckDBPyConnection = duckdb.connect(f"md:{warehouse_name}?motherduck_token={motherduck_token}")
    
    con.sql("create table if not exists main.properties as select * from polars_df")

    clean_properties(con)

    new_properties: pl.DataFrame = get_new_properties(con)

    # Format and send messages
    messages: List[str] = [format_property_message(row) for row in new_properties.to_dicts()]

    # Send messages in chunks of two
    for i in range(0, len(messages), 2):
        message_chunk: List[str] = messages[i:i+2]
        full_message: str = "\n\n".join(message_chunk)
        send_message(full_message)

if __name__ == "__main__":
    main()


