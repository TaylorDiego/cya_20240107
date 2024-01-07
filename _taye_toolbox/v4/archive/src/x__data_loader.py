import datetime
import time
import requests
from bs4 import BeautifulSoup
import json

def get_html(url):
    """Get the HTML from a URL"""
    response = requests.get(url)
    return response.text

def get_soup(html):
    """Get the soup from a URL"""
    soup = BeautifulSoup(html, 'html.parser')
    return soup

def get_title(soup):
    """Get the title from a URL"""
    title = soup.title.string
    return title

def clean_title(_title):
    """Remove invalid characters from title"""
    invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in invalid_chars:
        _title = _title.replace(char, '_').strip()
    return _title

def get_description(soup):
    """Get the description from a URL"""
    description = soup.find(attrs={"name": "description"})
    return description

def get_keywords(soup):
    """Get the keywords from a URL"""
    keywords = soup.find(attrs={"name": "keywords"})
    return keywords

def get_lists(soup):
    """Get the lists from a URL"""
    lists = soup.find_all('li')
    return lists

def get_text(soup):
    """Get the text from a URL"""
    paragraphs = soup.find_all('p')  # for paragraphs
    text = text = ' '.join([para.get_text().strip() for para in paragraphs])
    return text

def clean_text(text):
    """Remove non-ASCII characters from list of tokenized words"""
    return text.encode("ascii", errors="ignore").decode()

def save_text(_title, text):
    """Save the text to a file"""
    with open(f"..\\data\\inputs\\{_title}.txt", "w+", encoding='utf-8') as file:
        file.write(text)

def get_metadata(soup, url, c_title):
    """Get the metadata from a URL"""
    # title = get_title(soup)
    extraction_time = datetime.datetime.now().isoformat()
    _metadata = {"URL": url, "title": c_title, "datetime": extraction_time}
    return _metadata 

def save_metadata(title):
    """Save the metadata to a file"""
    with open(f"..\\data\\inputs\\{metadata['title']}_metadata.json", "w+", encoding='utf-8') as file:
        file.write(json.dumps(metadata, indent=4))

def main(url):
    """Get the text from a URL"""
    print("\nGreat! Let's get the text from that link.")
    time.sleep(1)
    html = get_html(url)
    soup = get_soup(html)
    title = get_title(soup)
    c_title = clean_title(title)
    text = get_text(soup)
    c_text = clean_text(text)
    save_text(c_title, c_text)
    metadata = get_metadata(soup, url)
    save_metadata(metadata)

if __name__ == "__main__":
    _url = input("\nPlease enter a URL: ")
    main(_url)


# def main(url):
#     """Get the text from a URL"""
#     print("\nGreat! Let's get the text from that link.")
#     time.sleep(1)
#     html = get_html(url)
#     soup = get_soup(html)
#     title = get_title(soup)
#     c_title = clean_title(title)
#     text = get_text(soup)
#     c_text = clean_text(text)
#     save_text(c_title, c_text)
#     # print(f"\nTitle: {c_title}")
#     # print(f"\n{c_text}")

# if __name__ == "__main__":
#     _url = input("\nPlease enter a URL: ")
#     main(_url)
#     # test = get_html("https://en.wikipedia.org/wiki/Python_(programming_language)")
#     # print(test)
#     # test = get_soup(test)
#     # print(test)
#     # test = get_text(test)
#     # print(test)