import requests
from bs4 import BeautifulSoup
import re
import logging
import polars
import duckdb
from scraper import parse_listing
from database import clean_properties, get_new_properties
from dotenv import load_dotenv
import os
from telegram_api import send_message, format_property_message



if __name__ == "__main__":


    load_dotenv()

    url = os.getenv("scrape_url")
    warehouse_name = os.getenv("warehouse_name")
    motherduck_token = os.getenv("motherduck_token")

    data = parse_listing(url)

    polars_df = polars.DataFrame(data)

    con = duckdb.connect(f"md:{warehouse_name}?motherduck_token={motherduck_token}")
    
    con.sql("create table if not exists main.properties as select * from polars_df")

    clean_properties(con)

    new_properties = get_new_properties(con)
    # Iterate over the DataFrame and format each property
    messages = [format_property_message(row) for row in new_properties.iter_rows(named=True)]

# Send messages in chunks of two
    for i in range(0, len(messages), 2):
        # Get the current chunk of two messages
        message_chunk = messages[i:i+2]
        # Join the two messages with a separator
        full_message = "\n\n".join(message_chunk)
        # Send the combined message
        send_message(full_message)


