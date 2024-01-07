"""Create the topic folders in the content store"""

import os
import json
import yaml

CONFIG = yaml.safe_load(open('..\\config\\config.yaml', 'r', encoding='utf-8'))
FOLDERS = CONFIG["FOLDERS"]

CONTENT_STORE = CONFIG["CONTENT_STORE"]
STORE_0 = CONFIG["STORE_0"]
STORE_1 = CONFIG["STORE_1"]
STORE_2 = CONFIG["STORE_2"]
STORE_3 = CONFIG["STORE_3"]
STORE_4 = CONFIG["STORE_4"]
STORE_5 = CONFIG["STORE_5"]

_content_stores = [STORE_0, STORE_1, STORE_2, STORE_3, STORE_4, STORE_5]

def read_json(filepath):
    """Read a JSON file"""
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def make_content_store_folders():
    """Make the content store folders"""
    for _store in _content_stores:
        base_directory = _store
        os.makedirs(base_directory, exist_ok=True)

def create_folders(directory, structure):
    """Create the folders in the content store"""
    for key, value in structure.items():
        folder_path = os.path.join(directory, key)
        os.makedirs(folder_path, exist_ok=True)
        if isinstance(value, dict):
            create_folders(folder_path, value)
        elif isinstance(value, list):
            for subfolder in value:
                subfolder_path = os.path.join(folder_path, subfolder)
                os.makedirs(subfolder_path, exist_ok=True)

def main():
    """Main function"""
    make_content_store_folders()
    folder_dict = read_json(FOLDERS)
    for _store in _content_stores:
        base_directory = _store
        create_folders(base_directory, folder_dict)
    print("\nDONE! CONTENT STORE folders are present, checked, and ready to go!")

if __name__=='__main__':
    main()