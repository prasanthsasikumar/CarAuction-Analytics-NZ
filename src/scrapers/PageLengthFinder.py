import requests
from bs4 import BeautifulSoup

def count_number_of_pages(url):
    # Send a GET request to the specified URL
    response = requests.get(url)

    # Check if the request was successful
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
