import logging


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
    con.sql(insert_query)
    con.sql("DELETE FROM main.properties;")


def get_new_properties(con) -> None:
    df = con.sql("SELECT * FROM main.new_properties;").pl()
    return df
