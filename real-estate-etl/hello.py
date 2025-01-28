import requests
from bs4 import BeautifulSoup

URL = "https://www.immobiliare.it/vendita-case/napoli/con-garage/?criterio=rilevanza&prezzoMinimo=340000&prezzoMassimo=700000&superficieMinima=100&boxAuto[]=3&boxAuto[]=4&boxAuto[]=1&tipoProprieta=1&fasciaPiano[]=30&fasciaPiano[]=20#geohash-sr605hm"

def main():
    response = requests.get(URL)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links on the page
        links = set()
        for a_tag in soup.find_all('a', class_='in-listingCardTitle', href=True):
            link = a_tag['href']
            print(link)
            links.add(link)


if __name__ == "__main__":
    main()
