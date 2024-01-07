"""(WIP - not functional) This script loads a URL and extracts the links (href) from it. It then saves the data into a JSON file."""

import json
import requests
from bs4 import BeautifulSoup

def fetch_html(url):
    """Fetch the HTML content of a given URL."""
    response = requests.get(url)
    return response.text

def parse_html(html_content):
    """Parse HTML and extract the required data."""
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {}

    # Extract section title
    section_title = soup.find('h1', class_='thread-list-view-title thread-subforum-title qa-page-title').text.strip()
    data[section_title] = {}

    # Adjust the search logic here based on the actual HTML structure
    # For example:
    # articles = soup.find_all('div', class_='article-class') # Replace 'article-class' with the actual class
    # for article in articles:
    #     article_name = article.find('h4').text.strip() # Adjust the tag and class if necessary
    #     article_link = article.find('a')['href']
    #     data[section_title][article_name] = article_link

    return data

def save_to_json(data, filename):
    """Save the extracted data to a JSON file."""
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

if __name__ == "__main__":
    url = input(f"\nEnter a URL: ")
    html_content = fetch_html(url)
    extracted_data = parse_html(html_content)
    save_to_json(extracted_data, 'output.json')
