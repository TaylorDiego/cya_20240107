import requests
from bs4 import BeautifulSoup, NavigableString
import json
from datetime import datetime
import unicodedata
import yaml

CONFIG = yaml.safe_load(open('..\\config\\config.yaml'))
CONTEXT = CONFIG["CONTEXT"]

def fetch_data(url):
    """Get the HTML from a URL"""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        return {"Error": str(e)}

def get_keywords(soup):
    """Get the keywords from a URL"""
    keywords = soup.find(attrs={"name": "keywords"})
    return keywords

def get_author(soup):
    try:
        # Find the <a> tag with the specified class and extract its text
        author_tag = soup.find('a', class_="username qa-username link link--quiet rank--bold")
        if author_tag:
            return author_tag.get_text(strip=True)
        else:
            return "Author not found"
    except Exception as e:
        return f"Error occurred: {e}"

def clean_title(soup):
    """Remove invalid characters from title"""
    c_title = soup.title.string
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        c_title = c_title.replace(char, '_').strip()
    return c_title

def extract_text(element):
    """Extracts the text from the given element"""
    if element.string:
        return element.string + ' '
    else:
        return ''.join(extract_text(child) for child in element.children if not isinstance(child, NavigableString))

def clean_text(soup):
    """Get the text from a URL"""
    paragraphs = soup.find_all('p')
    _text = ' '.join([extract_text(para).strip() for para in paragraphs])
    c_text = _text.encode("ascii", errors="ignore").decode()
    return c_text

def normalize_text(text):
    """Normalizes the text by removing extra spaces and special characters"""
    text = unicodedata.normalize('NFKC', text)
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = text.replace('\t', ' ')
    return text

def clean_lists(soup):
    """Get the lists from a URL"""
    structured_data = []
    for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        content = {
            'heading': normalize_text(heading.get_text().strip()), 
            'paragraphs': [], 
            'list': []
        }
        current_element = heading.next_sibling
        while current_element and not isinstance(current_element, NavigableString):
            if current_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                break
            if current_element.name == 'p':
                paragraph_text = normalize_text(current_element.get_text().strip())
                content['paragraphs'].append(paragraph_text)
            if current_element.name in ['ol', 'ul']:
                list_items = [normalize_text(li.get_text().strip()) for li in current_element.find_all('li')]
                content['list'] = list_items
                break
            current_element = current_element.next_sibling
        if content['list']:
            structured_data.append(content)
    return structured_data

def transform_data(soup, url):
    """Transforms the data into a JSON object"""
    if "Error" in soup:
        return soup

    c_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c_keywords = get_keywords(soup) if soup.find(attrs={"name": "keywords"}) else "No Keywords"
    c_title = clean_title(soup) if soup.title else "No Title"
    c_author = get_author(soup) if soup.find('a', class_="username qa-username link link--quiet rank--bold") else "No Author"
    c_text = clean_text(soup) if soup.text else "No Text"
    c_lists = clean_lists(soup) if soup.find_all(['ol', 'ul']) else "No Lists"

    data = {
        "URL": url
        , "DateTime": c_datetime
        , "Keywords": c_keywords
        , "Title": c_title
        , "Author": c_author
        , "Text": c_text
        , "Lists": c_lists
        # , "Headers": [header.get_text(strip=True) for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
    }
    return data

def save_data(data, filename=CONTEXT):
    """Saves the data into a JSON file."""
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# def user_requests():
#     input_url = input("\nEnter a URL: ")
#     _folder = input("\nPlease enter a folder name, for this url context: ")
#     if _folder[]
#     _category = input("\nPlease enter a category name, for this url context: ")

def main():
    """Get the text from a URL"""
    input_url = input("\nEnter a URL: ")
    soup = fetch_data(input_url)
    if "Error" not in soup:
        transformed_data = transform_data(soup, input_url)
        save_data(transformed_data)
        print(f"Data saved to {CONTEXT}")
    else:
        print(transformed_data["Error"])

if __name__ == "__main__":
    main()
