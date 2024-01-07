"""Get the text from a URL"""

import sys
from datetime import datetime
import json
import unicodedata
import requests
from bs4 import BeautifulSoup, NavigableString
import yaml
import get_sub_cat

CONFIG = yaml.safe_load(open('..\\config\\config.yaml', 'r', encoding='utf-8'))
FOLDERS = CONFIG["FOLDERS"]
CONTEXT = CONFIG["CONTEXT"]
STORE_1 = CONFIG["STORE_1"]

def read_folder_structure(file_path=FOLDERS):
    """Read a JSON file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

test = get_sub_cat.main()
print(test)

def store_content(_store, _subject, _category, _title):
    """Store the content in the content store"""
    store_content_file = (f"{_store}\\subjects\\{_subject}\\categories\\{_category}\\context__{_title}.json")
    return store_content_file


def fetch_data(url):
    """Get the HTML from a URL"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except requests.RequestException as e:
        return {"Error": str(e)}

def get_keywords(soup):
    """Get the keywords from a URL"""
    keywords = soup.find(attrs={"name": "keywords"})
    return keywords

def get_author(soup):
    """Get the author from a URL"""
    try:
        author_tag = soup.find('a', class_="username qa-username link link--quiet rank--bold") # Find the <a> tag with the specified class and extract its text
        if author_tag:
            return author_tag.get_text(strip=True)
        else:
            return "Author not found"
    except AttributeError as e:
        return f"AttributeError occurred: {e}"

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
    rm_login_msg = """Login Create an account Enter your username or e-mail address. We'll send you an e-mail with instructions to reset your password. Sorry, we're still checking this file's contents to make sure it's safe to download. Please try again in a few minutes. Sorry, our virus scanner detected that this file isn't safe to download."""
    paragraphs = soup.find_all('p')
    _text = ' '.join([extract_text(para).strip() for para in paragraphs])
    text = _text.replace(rm_login_msg, '')
    c_text = text.encode("ascii", errors="ignore").decode()
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

def transform_data(soup, url, title, text):
    """Transforms the data into a JSON object"""
    if "Error" in soup:
        return soup

    c_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c_keywords = get_keywords(soup) if soup.find(attrs={"name": "keywords"}) else "missing"
    c_title = clean_title(soup) if soup.title else "missing"
    c_author = get_author(soup) if soup.find('a', class_="username qa-username link link--quiet rank--bold") else "missing"
    c_text = clean_text(soup) if soup.text else "missing"
    c_lists = clean_lists(soup) if soup.find_all(['ol', 'ul']) else "missing"

    m_title = title
    m_text = text

    data = {
        "MANUAL_TITLE": m_title
        , "DateTime": c_datetime
        , "URL": url
        , "Keywords": c_keywords
        , "Title": c_title
        , "Author": c_author
        , "Text": c_text
        , "Lists": c_lists
        # , "Headers": [header.get_text(strip=True) for header in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
        , "MANUAL_TEXT": m_text
    }
    return data

def save_data(data, filename=CONTEXT):
    """Saves the data into a JSON file."""
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)

def save_content_store(data, filename, subject, category):
    pass

def user_input():
    input_url = input("\nEnter a URL: ")
    input_title = input("\nEnter page title: ")
    print("\nEnter page text please, and paste it here: \nNOTE: Type CTRL+Z and then ENTER to finish!") #print + stdin.read() to handle new line issues
    input_text = sys.stdin.read() #\nHINT: In FIREFOX, F9 = Reader Mode, then use Notepad to paste wihtout images (text only)...
    return input_url, input_title, input_text

def main():
    """Get the text from a URL"""
    input_url, input_title, input_text = user_input()
    soup = fetch_data(input_url)
    if "Error" not in soup:
        transformed_data = transform_data(soup, input_url,input_title, input_text)
        save_data(transformed_data, filename=CONTEXT)
        store_filename = (f"{CONFIG['STORE_1']}\\{input_title}.json")
        save_data(transformed_data, filename=CONFIG["ADD_CONTEXT"])
        print(f"\nDone!\n...context file saved {CONTEXT}")
    else:
        print(transformed_data["Error"])

if __name__ == "__main__":
    main()
