# Real Estate ETL

This repository uses BeautifulSoup to scrape real estate listings from the website of a local real estate agency.

It then cleans the data and loads it into DuckDB (Motherduck actually).

The cleaned_properties table holds the deduplicated data. 
The properties table holds the raw data and is cleaned up every run.
The new_properties table holds the delta of each run and is used to send new properties to the Telegram bot.

The goal of this work is to store historical property data and study price fluctuations and trends.