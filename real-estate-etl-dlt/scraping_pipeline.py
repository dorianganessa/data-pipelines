import logging
from typing import Any
import re
import dlt
import duckdb
from dlt.sources import DltResource

from scrapy import Spider  # type: ignore
from scrapy.http import Response  # type: ignore

from scraping import run_pipeline
from scraping.helpers import create_pipeline_runner

# Configure logging to display debug messages
logging.basicConfig(level=logging.ERROR)

class PropertySpider(Spider):
    name = "property_spider"  # Ensure the spider has a name

    def parse(self, response: Response, **kwargs: Any) -> Any:
        logging.debug("Parsing response from: %s", response.url)
        links = response.css('a.in-listingCardTitle::attr(href)').getall()
        for link in links:
            absolute_url = response.urljoin(link)
            logging.debug("Following link: %s", absolute_url)
            yield response.follow(absolute_url, callback=self.parse_page)

    def parse_page(self, response):
        logging.debug("Parsing page: %s", response.url)
        for listing in response.css('section.re-layoutContentCenter'):
            city = listing.css('div.re-title__content span.re-blockTitle__location::text').get()
            neighbourhood = listing.css('div.re-title__content span.re-blockTitle__location:nth-of-type(2)::text').get()
            road = listing.css('div.re-title__content span.re-blockTitle__location:nth-of-type(3)::text').get()
            price_raw = listing.css('div.re-overview__price span::text').get()
            price = self.parse_price(price_raw)
            square_meters_raw = listing.css('div.re-mainFeatures__item svg[viewBox="0 0 24 24"] + span::text').re_first(r'(\d+)\s?m²')
            square_meters = int(square_meters_raw) if square_meters_raw else None
            floor = listing.css('div.re-mainFeatures__item svg[viewBox="0 0 24 24"] + span::text').re_first(r'Piano\s(.+)')
            floor = floor.strip() if floor else None

            yield {
                "url": response.url,
                "title": response.css('title::text').get(),
                "content": response.css('p::text').getall(),
                "price": price,
                "city": city.strip() if city else None,
                "neighbourhood": neighbourhood.strip() if neighbourhood else None,
                "road": road.strip() if road else None,
                "square_meters": square_meters,
                "floor": floor,
            }

    @staticmethod
    def parse_price(price_raw):
        if not price_raw:
            return None
        price_cleaned = re.sub(r'[^\d]', '', price_raw)
        return int(price_cleaned) if price_cleaned else None

def scrape_properties() -> None:
    logging.debug("Starting property scraping")
    pipeline = dlt.pipeline(
        pipeline_name='main',
        destination='motherduck',
        dataset_name='main',
    )

    run_pipeline(
        pipeline,
        PropertySpider,
        scrapy_settings={
            "DEPTH_LIMIT": 1,
        },
        write_disposition="append",
    )
    logging.debug("Finished property scraping")

def clean_properties(con) -> None:
    logging.debug("Starting property cleaning")
    create_table_query = """
CREATE TABLE IF NOT EXISTS main.cleaned_properties (
    url TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    price INTEGER,
    city TEXT,
    neighbourhood TEXT,
    road TEXT,
    square_meters INTEGER,
    floor TEXT
);
CREATE OR REPLACE TABLE main.new_properties (
    url TEXT PRIMARY KEY,
    title TEXT,
    content TEXT,
    price INTEGER,
    city TEXT,
    neighbourhood TEXT,
    road TEXT,
    square_meters INTEGER,
    floor TEXT
);
"""
    con.sql(create_table_query)
    insert_query = """
INSERT INTO main.cleaned_properties (url, title, price, city, neighbourhood, road, square_meters, floor)
SELECT url, title, price, city, neighbourhood, road, square_meters, floor
FROM main.properties
WHERE NOT EXISTS (  
    SELECT 1 
    FROM main.cleaned_properties
    WHERE main.cleaned_properties.url = main.properties.url
);
"""
    insert_query_only_new = """
INSERT INTO main.new_properties (url, title, price, city, neighbourhood, road, square_meters, floor)
SELECT url, title, price, city, neighbourhood, road, square_meters, floor
FROM main.properties
WHERE NOT EXISTS (  
    SELECT 1 
    FROM main.cleaned_properties
    WHERE main.cleaned_properties.url = main.properties.url
)
"""
    con.sql(insert_query_only_new)
    print("Cleaning properties 3")
    con.sql(insert_query)
    print("Cleaning properties 4")
    con.sql("DELETE FROM main.properties;")
    print("Cleaning properties 5")

if __name__ == "__main__":
    print("Scraping properties")
    scrape_properties()
    print("Cleaning properties")

  #  con = duckdb.connect("md:adriano_warehouse")

   # clean_properties(con)
    
