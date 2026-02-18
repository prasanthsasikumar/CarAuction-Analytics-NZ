import requests
from bs4 import BeautifulSoup
import json

def scrape_vehicle_page(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
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
