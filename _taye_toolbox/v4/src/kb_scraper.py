"""Get the text from a URL"""

import time
import sys
import shutil
from datetime import datetime
import json
import unicodedata
import requests
from bs4 import BeautifulSoup, NavigableString
import yaml
import pandas as pd
# import get_sub_cat

class BaseWebScraper:
    def __init__(self, config_path=r'..\config\config.yaml'):
        self.CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.FOLDERS = self.CONFIG["FOLDERS"]
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_1 = self.CONFIG["STORE_1"]

    def read_folder_structure(self, file_path=None):
        """Read a JSON file"""
        if file_path is None:
            file_path = self.FOLDERS
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def fetch_data(self, url):
        """Get the HTML from a URL"""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.RequestException as e:
            return {"Error": str(e)}

    def get_keywords(self, soup):
        """Get the keywords from a URL"""
        keywords = soup.find(attrs={"name": "keywords"})
        return keywords

    def get_author(self, soup):
        """Get the author from a URL"""
        try:
            author_tag = soup.find('a', class_="username qa-username link link--quiet rank--bold") # Find the <a> tag with the specified class and extract its text
            if author_tag:
                return author_tag.get_text(strip=True)
            else:
                return "Author not found"
        except AttributeError as e:
            return f"AttributeError occurred: {e}"

    def clean_title(self, soup):
        """Remove invalid characters from title"""
        c_title = soup.title.string
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            c_title = c_title.replace(char, '_').strip()
        return c_title

    def extract_text(self, element):
        """Extracts the text from the given element"""
        if element.string:
            return element.string + ' '
        else:
            return ''.join(self.extract_text(child) for child in element.children if not isinstance(child, NavigableString))

    def clean_text(self, soup):
        """Get the text from a URL"""
        rm_login_msg = """Login Create an account Enter your username or e-mail address. We'll send you an e-mail with instructions to reset your password. Sorry, we're still checking this file's contents to make sure it's safe to download. Please try again in a few minutes. Sorry, our virus scanner detected that this file isn't safe to download."""
        paragraphs = soup.find_all('p')
        _text = ' '.join([self.extract_text(para).strip() for para in paragraphs])
        text = _text.replace(rm_login_msg, '')
        c_text = text.encode("ascii", errors="ignore").decode()
        return c_text

    def normalize_text(self, text):
        """Normalizes the text by removing extra spaces and special characters"""
        text = unicodedata.normalize('NFKC', text)
        text = text.replace('\u2018', "'").replace('\u2019', "'")
        text = text.replace('\t', ' ')
        return text

    def clean_lists(self, soup):
        """Get the lists from a URL"""
        structured_data = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            content = {
                'heading': self.normalize_text(heading.get_text().strip()), 
                'paragraphs': [], 
                'list': []
            }
            current_element = heading.next_sibling
            while current_element and not isinstance(current_element, NavigableString):
                if current_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    break
                if current_element.name == 'p':
                    paragraph_text = self.normalize_text(current_element.get_text().strip())
                    content['paragraphs'].append(paragraph_text)
                if current_element.name in ['ol', 'ul']:
                    list_items = [self.normalize_text(li.get_text().strip()) for li in current_element.find_all('li')]
                    content['list'] = list_items
                    break
                current_element = current_element.next_sibling
            if content['list']:
                structured_data.append(content)
        return structured_data

    def transform_data(self, soup, url):
        """Transforms the data into a JSON object"""
        if "Error" in soup:
            return soup

        c_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c_keywords = self.get_keywords(soup) if soup.find(attrs={"name": "keywords"}) else "missing"
        c_title = self.clean_title(soup) if soup.title else "missing"
        c_author = self.get_author(soup) if soup.find('a', class_="username qa-username link link--quiet rank--bold") else "missing"
        c_text = self.clean_text(soup) if soup.text else "missing"
        c_lists = self.clean_lists(soup) if soup.find_all(['ol', 'ul']) else "missing"

        data = {
             "DateTime": c_datetime
            , "URL": url
            , "Keywords": c_keywords
            , "Title": c_title
            , "Author": c_author
            , "Text": c_text
            , "Lists": c_lists
        }
        return data

    def save_context(self, data):
        """Saves the data into a JSON file."""
        # if filename is None:
        filename = self.CONTEXT
        with open(filename, 'w+', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    def main(self, _url):
        """Get the text from a URL, and format it for storage in the content store"""
        soup = self.fetch_data(_url)
        if "Error" not in soup:
            # _folder = ""
            # _category = ""
            # _title = ""
            # _type = ""
            transformed_data = self.transform_data(soup, _url)
            self.save_context(transformed_data)
            return transformed_data["Title"]
        else:
            # print(transformed_data["Error"])
            return "Error"

class UserScraper:
    def __init__(self, config_path=r'..\config\config.yaml'):
        self.CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_1 = self.CONFIG["STORE_1"]

    def user_input(self):
        input_url = input("\nEnter a URL: ")
        input_title = input("\nEnter page title: ")
        print("\nEnter page text please, and paste it here: \nNOTE: Type CTRL+Z and then ENTER to finish!") #print + stdin.read() to handle new line issues
        input_text = sys.stdin.read() #\nHINT: In FIREFOX, F9 = Reader Mode, then use Notepad to paste wihtout images (text only)...
        return input_url, input_title, input_text
    
    def main(self):
        self.user_input()

class BulkScraper:
    def __init__(self, config_path=r'..\config\config.yaml'):
        self.CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_1 = self.CONFIG["STORE_1"]
        self.KB_LINKS_TEST = self.CONFIG["KB_LINKS_TEST"]
        self.KB_LINKS = self.CONFIG["KB_LINKS"]

    def select_csv(self):
        """Select the CSV file"""
        _test_links = self.KB_LINKS_TEST
        _main_links = self.KB_LINKS
        _default = _test_links # _main_links
        print(f'You selected BULK MODE. Use the default {_default} or select a different path.')
        _choice = input("\nUse default path? \na: yes \nb: no\n\nPlease enter a or b: ")

        if _choice.strip().lower() == 'a':
            print("\nGreat! You selected the default path.")
            _path = _default
            return _path
        
        elif _default.strip().lower() == 'b':
            print("\nGreat! You selected a different path.")
            _path = input("\nEnter the path to the CSV file: ")
            return _path

    def load_csv(self, file_path):
        """Read a CSV file"""
        df = pd.read_csv(file_path)
        return df

    def save_to_store(self, _folder, _category, _title, _type):
        """Save the context file to the content store"""
        _store = self.STORE_1
        _file = "__context.json"
        _char_replace = ['?', '!', ':', ';', '.', ',', '/', '\\', '|', '*', "'", '"']
        for char in _char_replace:
            _title = _title.replace(char, '_').strip()
        c_title = _title.replace(' ', '_')
        # _filename = f'{_store}/subjects/{_folder}/categories/{_category}/{_type}/{c_title}{_file}'
        _filename = f'{_store}/subjects/{_folder}/categories/{_category}/{_type}_{c_title}{_file}'
        print(f'\nSaving to: {_filename}')
        shutil.copy(self.CONTEXT, _filename)

    def run_bulk_scraper(self, df):
        """Run the bulk scraper"""
        for idx, row in df.iterrows():
            time.sleep(.5)
            _type = row['type']
            _folder = row['folder']
            _category = row['category']
            _title = row['title']
            _url = row['url']

            print(f'\nrow: {idx + 1} out of {len(df)}')
            print(f'type: {_type} KNOW article')
            print(f'title: {_title}')
            print(f'folder: {_folder}; category: {_category}; url: {_url}')

            if _type == "WON'T":
                print(f'\nSkipping article {_type}, since labling it as WON\'T KNOW.')
                continue
            else:
                base_scraper = BaseWebScraper()
                base_scraper.main(_url)

                self.save_to_store(_folder, _category, _title, _type)

    def main(self):
        """Get the text from a URL, and format it for storage in the content store"""
        _path = self.select_csv()
        df = self.load_csv(_path)
        self.run_bulk_scraper(df)

class ScraperSelector():
    def __init__(self, config_path=r'..\config\config.yaml'):
        self.CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_1 = self.CONFIG["STORE_1"]

    def start_user(self):
        """Ask the user for input, a csv path or a url"""
        _scraper = input("\nSelect your method: \n\na: CSV (BULK MODE) \nb: URL (USER MODE)\n\nPlease enter a or b: ")

        if _scraper.strip().lower() == 'a':
            print("\nselected: BULK MODE...")
            bulk_scraper = BulkScraper()
            bulk_scraper.main()

        elif _scraper.strip().lower() == 'b':
            print("\nselected: USER MODE...")
            user_scraper = UserScraper()
            user_scraper.main()

        else:
            print("\nInvalid option. Please try again.")

    def main(self):
        """Get the text from a URL, and format it for storage in the content store"""
        self.start_user()


if __name__ == "__main__":
    scraper_selector = ScraperSelector()
    scraper_selector.start_user()