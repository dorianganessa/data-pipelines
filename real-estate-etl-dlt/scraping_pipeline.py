from typing import Any
import re
import dlt
import duckdb
from dlt.sources import DltResource
from scrapy import Spider  # type: ignore
from scrapy.http import Response  # type: ignore

from scraping import run_pipeline
from scraping.helpers import create_pipeline_runner

class PropertySpider(Spider):
    def parse(self, response: Response, **kwargs: Any) -> Any:
         # Extract links based on the rules
        links = response.css('a.in-listingCardTitle::attr(href)').getall()

        # Yield the links as data
        for link in links:
            absolute_url = response.urljoin(link)
            # Follow the link to scrape its content
            yield response.follow(absolute_url, callback=self.parse_page)

    def parse_page(self, response):
        # Customize the rules to scrape the page's content
        for listing in response.css('section.re-layoutContentCenter'):
            # Use more specific and robust selectors
            city = listing.css('div.re-title__content span.re-blockTitle__location::text').get()
            neighbourhood = listing.css('div.re-title__content span.re-blockTitle__location:nth-of-type(2)::text').get()
            road = listing.css('div.re-title__content span.re-blockTitle__location:nth-of-type(3)::text').get()
            price_raw = listing.css('div.re-overview__price span::text').get()
            price = self.parse_price(price_raw)
            # Extract square meters
            square_meters_raw = listing.css('div.re-mainFeatures__item svg[viewBox="0 0 24 24"] + span::text').re_first(r'(\d+)\s?m²')
            square_meters = int(square_meters_raw) if square_meters_raw else None

            # Extract floor information
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
        # Remove any non-numeric characters (except the decimal separator)
        price_cleaned = re.sub(r'[^\d]', '', price_raw)
        return int(price_cleaned) if price_cleaned else None


def scrape_properties() -> None:
    pipeline = dlt.pipeline(
        pipeline_name="scraping",
        destination="duckdb",
        dataset_name="properties",
    )

    run_pipeline(
        pipeline,
        PropertySpider,
        # you can pass scrapy settings overrides here
        scrapy_settings={
            "DEPTH_LIMIT": 1,
        },
        write_disposition="append",
    )

def clean_properties() -> None:
    create_table_query = """
CREATE TABLE IF NOT EXISTS properties.cleaned_properties (
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
CREATE OR REPLACE TABLE properties.new_properties (
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
    con = duckdb.connect("../scraping.duckdb")
    con.sql(create_table_query)

    insert_query = """
INSERT INTO properties.cleaned_properties (url, title, price, city, neighbourhood, road, square_meters, floor)
SELECT url, title, price, city, neighbourhood, road, square_meters, floor
FROM properties.properties
WHERE NOT EXISTS (  
    SELECT 1 
    FROM properties.cleaned_properties
    WHERE properties.cleaned_properties.url = properties.properties.url
);
"""

    insert_query_only_new = """
INSERT INTO properties.new_properties (url, title, price, city, neighbourhood, road, square_meters, floor)
SELECT url, title, price, city, neighbourhood, road, square_meters, floor
FROM properties.properties
WHERE NOT EXISTS (  
    SELECT 1 
    FROM properties.cleaned_properties
    WHERE properties.cleaned_properties.url = properties.properties.url
)
"""
    con.sql(insert_query_only_new)
    con.sql(insert_query)
 
    con.sql("DELETE FROM properties.properties;")


if __name__ == "__main__":
    scrape_properties()
    clean_properties()
    
