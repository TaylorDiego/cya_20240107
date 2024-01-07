"""This script contains functions to get the subject and category in order to store the KB context files properly."""

import string
import json
import yaml

CONFIG = yaml.safe_load(open('..\\config\\config.yaml', 'r', encoding='utf-8'))
FOLDERS = CONFIG["FOLDERS"]

def read_json(filepath):
    """Read a JSON file with error handling."""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading file: {e}")
        return None

def create_option_dict(options_list):
    """Create a dictionary from a list of options."""
    options_dict = {}
    for i, option in enumerate(options_list):
        if i < len(string.ascii_uppercase):
            key = string.ascii_uppercase[i]
            options_dict[key] = option
    return options_dict

def prompt_for_choice(options_dict, prompt_message):
    """Prompt user to make a choice from given options."""
    while True:
        for key, value in options_dict.items():
            print(f"{key}: {value}")

        choice = input(prompt_message).strip().upper()

        if choice in options_dict:
            confirmation_message = f"\nYou selected: < {options_dict[choice].upper()} > ...Is this correct? \na: yes \nb: no\n\nconfirm: "
            if input(confirmation_message).strip().lower() == 'a':
                return options_dict[choice]
        print("\nInvalid option. Please try again.")

def select_subject():
    """Select the subject."""
    print("\nPlease select a KB subject area to store this file in:")
    _folders = read_json(FOLDERS)
    if _folders:
        return prompt_for_choice(create_option_dict(_folders["subjects"]), "\nPlease enter a valid subject: ")

def auto_select_category(options_dict, prompt_message, auto_select_single_option=False):
    """Auto-select if there's only one category option."""
    if auto_select_single_option and len(options_dict) == 1:
        single_key = next(iter(options_dict))
        print(f"\nOnly one option available: {options_dict[single_key]}")
        confirmation_message = f"\nOnly one (1) option available: auto-selected: < {options_dict[single_key].upper()} > ...Is this correct? \na: yes \nb: no\n\nconfirm: "
        if input(confirmation_message).strip().lower() == 'a':
            return options_dict[single_key]
        
    while True:
        for key, value in options_dict.items():
            print(f"{key}: {value}")

        choice = input(prompt_message).strip().upper()

        if choice in options_dict:
            confirmation_message = f"\nYou selected: < {options_dict[choice].upper()} > ...Is this correct? \na: yes \nb: no\n\nconfirm: "
            if input(confirmation_message).strip().lower() == 'a':
                return options_dict[choice]

        print("Invalid option. Please try again.")

def select_category(_subject):
    """Select the category, auto-selecting if only one option is available."""
    print(f"\nPlease select a {_subject} category:")
    _folders = read_json(FOLDERS)
    if _folders and _subject in _folders["subjects"]:
        categories = _folders["subjects"][_subject]["categories"]
        return auto_select_category(create_option_dict(categories), "\nPlease enter a valid category: ", auto_select_single_option=True)

def main():
    """Main function."""
    _subject = select_subject()
    if _subject:
        _category = select_category(_subject)
        if _category:
            return _subject, _category
    return None, None

if __name__ == "__main__":
    _subject, _category = main()
    if _subject and _category:
        print(f"\nSubject: {_subject}, Category: {_category} \n\nDONE!")
    else:
        print("\nFailed to select valid subject and category.")