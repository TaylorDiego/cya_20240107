
"""This script loads a URL and extracts the text from it. It then saves the data into a JSON file."""

import sys
from datetime import datetime
import json
import unicodedata
import requests
from bs4 import BeautifulSoup, NavigableString
import yaml
import get_sub_cat

class UrlLoader:
    def __init__(self, config_path='..\config\config.yaml'):
        self.config = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.folders = self.config["FOLDERS"]
        self.context = self.config["CONTEXT"]
        self.store_1 = self.config["STORE_1"]

    def read_folder_structure(self, file_path=None):
        if file_path is None:
            file_path = self.folders
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def store_content(self, _store, _subject, _category, _title):
        store_content_file = (f"{_store}\subjects\{_subject}\categories\{_category}\context__{_title}.json")
        return store_content_file

    def fetch_data(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.RequestException as e:
            return {"Error": str(e)}

    def get_keywords(self, soup):
        keywords = soup.find(attrs={"name": "keywords"})
        return keywords

    def get_author(self, soup):
        try:
            author_tag = soup.find('a', class_="username qa-username link link--quiet rank--bold")
            if author_tag:
                return author_tag.get_text(strip=True)
            else:
                return "Author not found"
        except AttributeError as e:
            return f"AttributeError occurred: {e}"

    def clean_title(self, soup):
        c_title = soup.title.string
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        for char in invalid_chars:
            c_title = c_title.replace(char, '')
        return c_title

    # Additional methods based on the other functions in the script...
    
    def user_input(self):
        input_url = input("\nEnter a URL: ")
        input_title = input("\nEnter page title: ")
        print("\nEnter page text please, and paste it here: \nNOTE: Type CTRL+Z and then ENTER to finish!")
        input_text = sys.stdin.read()
        return input_url, input_title, input_text

    def main(self):
        input_url, input_title, input_text = self.user_input()
        soup = self.fetch_data(input_url)
        if "Error" not in soup:
            transformed_data = self.transform_data(soup, input_url, input_title, input_text)
            self.save_data(transformed_data, filename=self.context)
            store_filename = f"{self.config['STORE_1']}\{input_title}.json"
            self.save_data(transformed_data, filename=self.config["ADD_CONTEXT"])
            print(f"\nDone!\n...context file saved {self.context}")
        else:
            print(transformed_data["Error"])

if __name__ == "__main__":
    url_loader = UrlLoader()
    url_loader.main()
