import requests
from bs4 import BeautifulSoup
import time

def count_number_of_pages(url):
    # Headers to mimic a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://manheim.co.nz/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin'
    }
    
    # Retry logic with exponential backoff
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Send a GET request to the specified URL with timeout
            response = requests.get(url, headers=headers, timeout=30)
            
            # Check if the request was successful
            if response.status_code == 200:
                break
            elif attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"Got status {response.status_code}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 5
                print(f"Request failed: {e}, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                print(f"Failed after {max_retries} attempts: {e}")
                return 0
    
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the <ul> tag with class="pages"
        ul_tag = soup.find('ul', class_='pages')

        if ul_tag:
            # Count the number of <li> tags inside the <ul>
            li_count = len(ul_tag.find_all('li'))
            print(f"Number of <li> tags inside <ul class='pages'>: {li_count}")
            return li_count
        else:
            print("No <ul> tag with class='pages' found on the page.")
            return 0
    else:
        print("Failed to retrieve the webpage.")
        return 0

# Test the function with the given URL
url = "https://manheim.co.nz/damaged-vehicles/search?PageNumber=1&RecordsPerPage={}&searchType=Z&page={}"

N = 120  # Specify the value of N here
pageNumber = 1  # Specify the value of page here

# Format the URL with the values of N and page
formatted_url = url.format(N, pageNumber)
count_number_of_pages(formatted_url)
