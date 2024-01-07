"""Get the text from a URL"""

import sys
from datetime import datetime
import json
import unicodedata
import requests
from bs4 import BeautifulSoup, NavigableString
import yaml
# import get_sub_cat

class UrlLoader:
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

    def store_content(self, _store, _subject, _category, _title):
        """Store the content in the content store"""
        store_content_file = (f"{_store}\\subjects\\{_subject}\\categories\\{_category}\\context__{_title}.json")
        return store_content_file

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

    def transform_data(self, soup, url, title, text):
        """Transforms the data into a JSON object"""
        if "Error" in soup:
            return soup

        c_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c_keywords = self.get_keywords(soup) if soup.find(attrs={"name": "keywords"}) else "missing"
        c_title = self.clean_title(soup) if soup.title else "missing"
        c_author = self.get_author(soup) if soup.find('a', class_="username qa-username link link--quiet rank--bold") else "missing"
        c_text = self.clean_text(soup) if soup.text else "missing"
        c_lists = self.clean_lists(soup) if soup.find_all(['ol', 'ul']) else "missing"

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

    def save_data(self, data, filename=None):
        """Saves the data into a JSON file."""
        if filename is None:
            filename = self.CONTEXT
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    # def save_data(self, data, filename=CONTEXT):
    #     """Saves the data into a JSON file."""
    #     with open(filename, 'w', encoding='utf-8') as file:
    #         json.dump(data, file, indent=4)

    def save_content_store(self, data, filename, subject, category):
        pass

    def user_input(self):
        input_url = input("\nEnter a URL: ")
        input_title = input("\nEnter page title: ")
        print("\nEnter page text please, and paste it here: \nNOTE: Type CTRL+Z and then ENTER to finish!") #print + stdin.read() to handle new line issues
        input_text = sys.stdin.read() #\nHINT: In FIREFOX, F9 = Reader Mode, then use Notepad to paste wihtout images (text only)...
        return input_url, input_title, input_text
    


    def select_input_type():
        """Select the input type"""
        pass

    def main(self, bulk=False):
        """Get the text from a URL, defaulting to a user input for url and content if bulk=False"""
        if bulk==False:
            input_url, input_title, input_text = self.user_input()
            soup = self.fetch_data(input_url)
            if "Error" not in soup:
                transformed_data = self.transform_data(soup, input_url, input_title, input_text)
                self.save_data(transformed_data, filename=self.CONTEXT)
                # store_filename = (f"{self.CONFIG['STORE_1']}\\{input_title}.json")
                self.save_data(transformed_data, filename=self.CONFIG["ADD_CONTEXT"])
                print(f"\nDone!\n...context file saved {self.CONTEXT}")
            else:
                print(transformed_data["Error"])
        elif bulk==True:
            for row in self.bulk_input():
                input_url, input_title, input_text = row
                soup = self.fetch_data(input_url)

    def bulk_input(self):
        """Bulk input from a csv"""
        pass

if __name__ == "__main__":
    url_loader = UrlLoader()
    url_loader.main()