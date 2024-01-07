"""(WIP - not functional) This script loads a URL and extracts the links (href) from it. It then saves the data into a JSON file."""

import json
import requests
from bs4 import BeautifulSoup

def fetch_html(_url):
    """Fetch the HTML content of a given URL."""
    response = requests.get(_url, timeout=10)
    # print(f'Fetched HTML from {response.text}')  # Debugging line
    return response.text

def parse_html(_html_content):
    """Parse HTML and extract the required data."""
    soup = BeautifulSoup(_html_content, 'html.parser')
    articles = []

    list_items = soup.find_all('li', class_='topic-curation__item')
    print(f'Found {len(list_items)} list items')  # Debugging line

    for li in list_items:
        article = {}
        title_element = li.find('h4', class_='topic-curation__title thread-list-block__title')
        author_element = li.find('a', class_='topic-curation__item-type-link')
        link_element = li.find('a', class_='topic-curation__item-link link')

        if title_element is not None:
            article['title'] = title_element.text.strip()
        else:
            print('Title element not found')  # Debugging line

        if author_element is not None:
            article['author'] = author_element.text.strip()
        else:
            print('Author element not found')  # Debugging line

        if link_element is not None:
            article['link'] = link_element.get('href')
        else:
            print('Link element not found')  # Debugging line

        if article:
            articles.append(article)

    return articles

# def parse_html(_html_content):
#     """Parse HTML and extract the required data."""
#     soup = BeautifulSoup(_html_content, 'html.parser')
#     data = {}

#     # Extract section title
#     section_title = soup.find('h1', class_='thread-list-view-title thread-subforum-title qa-page-title').text.strip()
#     data[section_title] = {}

#     # Adjust the search logic here based on the actual HTML structure
#     # For example:
#     # articles = soup.find_all('div', class_='article-class') # Replace 'article-class' with the actual class
#     # for article in articles:
#     #     article_name = article.find('h4').text.strip() # Adjust the tag and class if necessary
#     #     article_link = article.find('a')['href']
#     #     data[section_title][article_name] = article_link

#     return data

def save_to_json(data, filename):
    """Save the extracted data to a JSON file."""
    with open(filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

def main():
    """Main function."""
    url = input("\nEnter a URL: ")
    html_content = fetch_html("raw_for_parse.htm")
    extracted_data = parse_html(html_content)
    save_to_json(extracted_data, 'output.json')

if __name__ == "__main__":
    main()
    # url = input("\nEnter a URL: ")
    # html_content = fetch_html(url)
    # extracted_data = parse_html(html_content)
    # save_to_json(extracted_data, 'output.json')
