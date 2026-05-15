import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_fuel_prices():
    # Using the European page as it has a very stable table structure
    url = "https://www.e-petrol.pl/notowania/rynki-zagraniczne/stacje-paliw-europa"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Default fallbacks (May 2026 estimated averages)
    fuel_data = {
        "pb95": "6.28", 
        "on": "6.81",
        "lpg": "3.78",
        "updated": datetime.now().strftime("%Y-%m-%d")
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the tables on the page
        tables = soup.find_all('table')
        
        if not tables:
            print("No tables found. Site might be blocking us. Using fallbacks.")
        else:
            # Table 0 is usually Pb95, Table 1 is Diesel
            for i, table in enumerate(tables[:2]):
                rows = table.find_all('tr')
                for row in rows:
                    if "POLSKA" in row.text.upper():
                        cols = row.find_all('td')
                        # On this specific page, the price in PLN is usually the last column
                        price = cols[-1].text.strip().replace(',', '.')
                        if i == 0: fuel_data["pb95"] = price
                        if i == 1: fuel_data["on"] = price

        with open('prices.json', 'w') as f:
            json.dump(fuel_data, f, indent=4)
        print(f"Success! Updated prices: Pb95: {fuel_data['pb95']}, ON: {fuel_data['on']}")

    except Exception as e:
        print(f"Critical Error: {e}. Writing fallbacks to prices.json.")
        with open('prices.json', 'w') as f:
            json.dump(fuel_data, f, indent=4)

if __name__ == "__main__":
    scrape_fuel_prices()