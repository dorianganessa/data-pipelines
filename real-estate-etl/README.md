# Real Estate ETL

This repository uses BeautifulSoup to scrape real estate listings from the website of a local real estate agency.

It then cleans the data and loads it into DuckDB (Motherduck actually).

The cleaned_properties table holds the deduplicated data. 
The properties table holds the raw data and is cleaned up every run.
The new_properties table holds the delta of each run and is used to send new properties to the Telegram bot.

The goal of this work is to store historical property data and study price fluctuations and trends.

## Setup

To run the project locally, create a .env file in the root directory with the following variables:

warehouse_name=
motherduck_token=
scrape_url=
telegram_bot_api_key=
chat_id=
chat_tag=

You can get a new motherduck token after creating an account [here](https://motherduck.com/).

You can get the telegram bot api key by creating a new bot on telegram and using the token provided by BotFather.

You can get the chat id by using the telegram bot @usinfobot.

You can get the scrape url by going to [the real estate website](https://www.immobiliare.it/) and using the search functionality.

## Running the project

To run the project, use the following command:

```bash
uv run scan_properties.py
```

you need to install [uv](https://docs.astral.sh/uv/) to run the project.

