"""This script contains functions to save data to files."""

import json
import yaml

CONFIG = yaml.safe_load(open('..\\config\\config.yaml', 'r', encoding='utf-8'))
# CONTEXT = CONFIG["CONTEXT"]
# ADD_CONTEXT = CONFIG["ADD_CONTEXT"]
# RAW_QUIZ = CONFIG["RAW_QUIZ"]
# RAW_ANSWER_KEY = CONFIG["RAW_ANSWER_KEY"]
# AI_QUIZ = CONFIG["AI_QUIZ"]
# QA_REPORT = CONFIG["QA_REPORT"]
# AI_ANSWER_KEY =  CONFIG["AI_ANSWER_KEY"]
# HUMAN_QUIZ = CONFIG["HUMAN_QUIZ"]
# HUMAN_ANSWER_KEY = CONFIG["HUMAN_ANSWER_KEY"]
# FINAL_QUIZ = CONFIG["FINAL_QUIZ"]
# FINAL_ANSWER_KEY = CONFIG["FINAL_ANSWER_KEY"]
# TESTINVITE = CONFIG["TESTINVITE"]

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)
    
def save_json(_json, file_path):
    with open(file_path, 'w+', encoding='utf-8') as file:
        json.dump(_json, file, indent=4)

def save_txt(_content, filepath):
    with open(filepath, 'w+', encoding='utf-8') as file: # "a+ MEANS append, w+ MEANS create/overwrite"
        file.write(_content)

def save_csv(_content, filepath):
    with open(filepath, 'w+', encoding='utf-8') as file: # "a+ MEANS append, w+ MEANS create/overwrite"
        file.write(_content)

# def main():
#     pass

# if __name__=='__main__':
#     main()