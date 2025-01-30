import re
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List


def parse_price(price_raw: Optional[str]) -> Optional[int]:
    if not price_raw:
        return None
    price_cleaned = re.sub(r'[^\d]', '', price_raw)
    return int(price_cleaned) if price_cleaned else None

def parse_page(url: str) -> Dict[str, Optional[any]]:
    logging.debug("Parsing page: %s", url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    listings = soup.select('section.re-layoutContentCenter')
    
    for listing in listings:
        city = listing.select_one('div.re-title__content span.re-blockTitle__location')
        neighbourhood = listing.select_one('div.re-title__content span.re-blockTitle__location:nth-of-type(2)')
        road = listing.select_one('div.re-title__content span.re-blockTitle__location:nth-of-type(3)')
        price_raw = listing.select_one('div.re-overview__price span')
        price = parse_price(price_raw.text if price_raw else None)
        
        square_meters_match = re.search(r'(\d+)\s?m²', soup.text)
        square_meters = int(square_meters_match.group(1)) if square_meters_match else None
        
        floor_match = re.search(r'Piano\s(\d+)', soup.text)
        floor = int(floor_match.group(1)) if floor_match else None

        # Find the feature item related to parking/garage
        garage_feature = listing.find('dt', class_='re-featuresItem__title', string="Box, posti auto")

        if garage_feature:
            # Get the associated description (dd)
            garage_description = garage_feature.find_next('dd', class_='re-featuresItem__description')
            garage_info = garage_description.get_text(strip=True) if garage_description else None
        else:
            garage_info = None
        
        data = {
            "url": url,
            "title": soup.title.string if soup.title else None,
            "content": [p.text.strip() for p in soup.find_all('p')],
            "price": price,
            "city": city.text.strip() if city else None,
            "neighbourhood": neighbourhood.text.strip() if neighbourhood else None,
            "road": road.text.strip() if road else None,
            "square_meters": square_meters,
            "floor": floor,
            "garage_info": garage_info,
        }
        
    return data

def parse_listing(url: str) -> List[Dict[str, Optional[any]]]:
    logging.debug("Fetching main listing page: %s", url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_list = []
    links = soup.select('a.in-listingCardTitle')
    for link in links:
        absolute_url = requests.compat.urljoin(url, link['href'])
        logging.debug("Following link: %s", absolute_url)
        data_list.append(parse_page(absolute_url))
    return data_list
