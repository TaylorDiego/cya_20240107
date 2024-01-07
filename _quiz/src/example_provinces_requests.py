"""Example of using OpenAI to get facts about provinces, using requests"""

import time
import json
import asyncio
import aiohttp
import yaml
import requests
# from openai import OpenAI

config_path=r'..\config\config.yaml'

provinces = ["Ontario", "British Columbia"] #, "Alberta", "Quebec", "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island", "Northwest Territories", "Nunavut", "Yukon"]
province_facts = {}
CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))

KEYS = yaml.safe_load(open(CONFIG["KEYS"], 'r', encoding='utf-8'))
OPENAI_API_KEY = KEYS["OPENAI_API_KEY"]
# client = OpenAI(api_key=OPENAI_API_KEY)

def province_year(province_name):
    """Get the year a province was founded"""
    payload = {
        "model": "gpt-3.5-turbo"
        , "temperature": 0
        , "max_tokens": 200
        , "messages": [
            {"role": "system", "content": "You are an expert in Canadian history."}
            , {"role": "user", "content": f"What year was {province_name} named the current name (as of last information cut-off date)?"}
            , {"role": "system", "content": "Please keep your answer short and to the point."}
        ]
    }
    _headers = {"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_API_KEY}"}
    response = requests.post("https://api.openai.com/v1/chat/completions", data=json.dumps(payload), headers=_headers, timeout=5).json()
    # print(response)
    if 'choices' in response:
        result = response['choices'][0]['message']['content']
        return result
    else:
        return "Error: " + response['error']['message']

def run_facts():
    """Run the facts"""
    for province in provinces:
        # print(f"\nGetting facts for: {province}")
        province_facts[province] = province_year(province)
    return province_facts

def start_user():
    """Start the user"""
    print("Let's learn about Canadian history!\n")

def main():
    """Run the main program"""
    start_user()
    facts = run_facts()
    print("\nHere are the facts about Provinces:")
    for k, v in facts.items():
        print(f"\nProvince: {k}\n Fact: {v}")

if __name__ == "__main__":
    time_start = time.perf_counter()
    main()
    time_end = time.perf_counter()
    print(f"\nPERFORMANCE: Time to run: {time_end - time_start:0.4f} seconds")