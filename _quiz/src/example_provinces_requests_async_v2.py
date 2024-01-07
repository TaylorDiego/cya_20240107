"""Example of using OpenAI to get facts about provinces, using requests"""

import time
import json
import asyncio
import nest_asyncio
import aiohttp
import yaml

nest_asyncio.apply()

config_path = r'..\config\config.yaml'
provinces = ["Ontario", "British Columbia", "Alberta", "Quebec", "Manitoba", "Saskatchewan", 
             "Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island", 
             "Northwest Territories", "Nunavut", "Yukon"]
province_facts = {}
CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
KEYS = yaml.safe_load(open(CONFIG["KEYS"], 'r', encoding='utf-8'))
OPENAI_API_KEY = KEYS["OPENAI_API_KEY"]

async def build_payload(province_name):
    """Build the payload for a province"""
    payload = {
        "model": "gpt-3.5-turbo",
        "temperature": 0,
        "max_tokens": 200,
        "messages": [
            {"role": "system", "content": "You are an expert in Canadian history."},
            {"role": "user", "content": f"What year was {province_name} named the current name (as of last information cut-off date)?"},
            {"role": "system", "content": "Please keep your answer short and to the point."}
        ]
    }
    return payload

async def get_tasks(session):
    """Get the tasks"""
    tasks = []
    _headers = {"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_API_KEY}"}
    for province_name in provinces:
        payload = await build_payload(province_name)
        task = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
        tasks.append((province_name, task))
    return tasks

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = await get_tasks(session)
        responses = await asyncio.gather(*(task for _, task in tasks))
        for (province_name, _), response in zip(tasks, responses):
            response = await response.json()
            if 'choices' in response:
                province_facts[province_name] = response['choices'][0]['message']['content']

if __name__ == "__main__":
    time_start = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - time_start

    print(f"\nHere are the facts about Provinces:")
    for k, v in province_facts.items():
        print(f"\nProvince: {k} \nFact: {v}")

    print(f"PERFORMANCE: Time elapsed: {elapsed:0.2f} seconds")