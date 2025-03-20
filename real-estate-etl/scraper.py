import re
import logging
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
import urllib.request
import ssl
import gzip
import os

def parse_price(price_str):
    if not price_str:
        return None
    price_match = re.search(r'\d+[.,]?\d*', price_str.replace('\u20ac', '').replace('.', '').replace(',', '.'))
    return int(price_match.group(0).split('.')[0]) if price_match else None



def parse_page(url: str) -> Dict[str, Optional[any]]:
    logging.debug("Parsing page: %s", url)

    proxy_url = os.getenv('proxy_url')
    
    # Create a context that doesn't verify certificates
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler({
            'http': proxy_url,
            'https': proxy_url
        }),
        urllib.request.HTTPSHandler(context=ctx)  # Add the SSL context
    )
    opener.addheaders = [
        ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'),
        ('Accept-Language', 'en-US,en;q=0.9'),
        ('Accept-Encoding', 'gzip, deflate, br'),
        ('Connection', 'keep-alive'),
        ('Upgrade-Insecure-Requests', '1'),
        ('Sec-Fetch-Dest', 'document'),
        ('Sec-Fetch-Mode', 'navigate'),
        ('Sec-Fetch-Site', 'none'),
        ('Sec-Fetch-User', '?1'),
    ]
    
    response = opener.open(url)
    
    # Check if response is gzipped
    if response.info().get('Content-Encoding') == 'gzip':
        import gzip
        html_content = gzip.decompress(response.read()).decode('utf-8', errors='replace')
    else:
        html_content = response.read().decode('utf-8', errors='replace')
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    listings = soup.select('section.ld-layoutContentCenter')
    for listing in listings:
        # Extract title, city, neighborhood, road
        title = soup.find('meta', property='og:title')
        city, neighbourhood, road = None, None, None
        if title:
            location_parts = title["content"].split('|')[0].split(', ')
            location_parts = [part.strip() for part in location_parts]
            if len(location_parts) >= 3:
                road, neighbourhood, city = location_parts[:3]
            elif len(location_parts) == 2:
                neighbourhood, city = location_parts[:2]
            elif len(location_parts) == 1:
                city = location_parts[0]
            
            # Remove unwanted "Appartamento" prefix if present in the road name
            if road and road.lower().startswith("appartamento"):
                road = road.replace("Appartamento", "").strip()
        
        # Extract price from the correct div
        price_span = soup.select_one('div.ld-overview__price span')
        price = parse_price(price_span.text if price_span else None)
        # Extract square meters
        square_meters_match = re.search(r'(\d+)\s?m²', soup.text)
        square_meters = int(square_meters_match.group(1)) if square_meters_match else None
        
        # Extract floor
        floor_match = re.search(r'Piano\s(\d+)', soup.text)
        floor = int(floor_match.group(1)) if floor_match else None
        
        # Extract garage info
        garage_info = None
        garage_feature = soup.find('dt', string=re.compile(r'Box|Posti auto', re.IGNORECASE))
        if garage_feature:
            garage_description = garage_feature.find_next('dd')
            garage_info = garage_description.get_text(strip=True) if garage_description else None
        
        # Extract content description
        description_paragraphs = [p.text.strip() for p in soup.find_all('p')]
        
        data = {
            "url": url,
            "title": soup.title.string if soup.title else None,
            "content": description_paragraphs,
            "price": price,
            "city": city,
            "neighbourhood": neighbourhood,
            "road": road,
            "square_meters": square_meters,
            "floor": floor,
            "garage_info": garage_info,
        }
        return data
   

def parse_listing(url: str) -> List[Dict[str, Optional[any]]]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    logging.debug("Fetching main listing page: %s", url)
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    data_list = []
    links = soup.select('a.in-listingCardTitle')
    for link in links:
        absolute_url = requests.compat.urljoin(url, link['href'])
        logging.debug("Following link: %s", absolute_url)
        data_list.append(parse_page(absolute_url))
    return data_list
