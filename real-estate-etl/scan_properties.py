import requests
from bs4 import BeautifulSoup
import re
import logging
import polars
import duckdb
from scraper import parse_listing
from database import clean_properties
from dotenv import load_dotenv
import os




if __name__ == "__main__":


    load_dotenv()

    url = os.getenv("scrape_url")
    warehouse_name = os.getenv("warehouse_name")
    motherduck_token = os.getenv("motherduck_token")

    data = parse_listing(url)

    polars_df = polars.DataFrame(data)
    print(polars_df)

    con = duckdb.connect(f"md:{warehouse_name}?motherduck_token={motherduck_token}")
    
    con.sql("create table if not exists main.properties as select * from polars_df")

    clean_properties(con)




