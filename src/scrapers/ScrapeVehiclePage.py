import requests
from bs4 import BeautifulSoup
import json
import time

def scrape_vehicle_page(url):
    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://manheim.co.nz/damaged-vehicles/search',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin'
    }
    
    # Retry logic with exponential backoff
    max_retries = 3
    response = None
    for attempt in range(max_retries):
        try:
            # Send a GET request to the URL with timeout
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                break
            elif attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"Vehicle page got status {response.status_code}, retrying in {wait_time}s...")
                time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"Vehicle page request failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"Failed to fetch vehicle page after {max_retries} attempts")
                return json.dumps({"Vehicle Comments": "N/A", "Vehicle Location": "N/A", "Vehicle Info": "N/A", "Vehicle Details": "N/A", "Vehicle Damage": "N/A"})
    
    if not response or response.status_code != 200:
        return json.dumps({"Vehicle Comments": "N/A", "Vehicle Location": "N/A", "Vehicle Info": "N/A", "Vehicle Details": "N/A", "Vehicle Damage": "N/A"})
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Create a dictionary to store the attribute values
    vehicle_data = {}

    # Find the section with class "vehicle-comments"
    vehicle_comments_section = soup.find("section", class_="vehicle-comments")
    vehicle_data["Vehicle Comments"] = ", ".join(vehicle_comments_section.stripped_strings) if vehicle_comments_section else "N/A"
    
    # Find the section with class "vehicle-item-location"
    vehicle_location_section = soup.find("section", class_="vehicle-item-location")
    vehicle_data["Vehicle Location"] = ", ".join(vehicle_location_section.stripped_strings) if vehicle_location_section else "N/A"
    
    # Find the section with class "vehicle-info"
    vehicle_info_section = soup.find("section", class_="vehicle-info")
    vehicle_info = ", ".join(map(lambda x: x.replace(':', '') if ':' in x else x, vehicle_info_section.stripped_strings)) if vehicle_info_section else "N/A"
    vehicle_data["Vehicle Info"] = vehicle_info


    # Find the section with class "vehicle-details"
    vehicle_details_section = soup.find("section", class_="vehicle-details")
    vehicle_details = ", ".join(map(lambda x: x.replace(':', '') if ':' in x else x, vehicle_details_section.stripped_strings)) if vehicle_details_section else "N/A"
    vehicle_details = vehicle_details.replace("\r\n                                ", "")
    vehicle_data["Vehicle Details"] = vehicle_details

    # Find the section with class "vehicle-damage"
    vehicle_damage_section = soup.find("section", class_="vehicle-damage")
    vehicle_damage = ", ".join(map(lambda x: x.replace(':', '') if ':' in x else x, vehicle_damage_section.stripped_strings)) if vehicle_damage_section else "N/A"
    vehicle_data["Vehicle Damage"] = vehicle_damage

    # Convert the dictionary to a JSON string
    json_data = json.dumps(vehicle_data, indent=4)

    # Return the JSON string
    return json_data

# Example usage:
url = "https://manheim.co.nz/damaged-vehicles/000000000006640001/2018-suzuki-swift-glc-1-2p-cvt-hatch?referringPage=SearchResults"
json_data = scrape_vehicle_page(url)
#print(json_data)
