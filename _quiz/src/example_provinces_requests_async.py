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

async def get_tasks(session):
    """Get the tasks"""
    tasks = []
    _headers = {"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_API_KEY}"}
    for province_name in provinces:
        print(f"\nGetting facts for: {province_name}")
        payload = {
            "model": "gpt-4",
            "temperature": 0,
            "max_tokens": 200,
            "messages": [
                {"role": "system", "content": "You are an expert in Canadian history."},
                {"role": "user", "content": f"What year was {province_name} named the current name (as of last information cut-off date)?"}, 
                {"role": "system", "content": "Please keep your answer short and to the point."}
            ]
        }
        tasks.append(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
    return tasks

async def province_year():
    """Get the year a province was founded"""
    async with aiohttp.ClientSession() as session:
        tasks = await get_tasks(session)
        responses = await asyncio.gather(*tasks)
        for province_name, response in zip(provinces, responses):
            response = await response.json()
            if 'choices' in response:
                province_facts[province_name] = response['choices'][0]['message']['content']
    return province_facts

async def main():
    facts = await province_year()
    print(f"\nHere are the facts about Provinces: {facts}")

if __name__ == "__main__":
    time_start = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - time_start

    print(f"\nHere are the facts about Provinces:")
    for k, v in province_facts.items():
        print(f"\nProvince: {k} \nFact: {v}")

    print(f"Time elapsed: {elapsed:0.2f} seconds")


# """Example of using OpenAI to get facts about provinces, using requests"""

# import time
# import json
# import asyncio
# import nest_asyncio
# import aiohttp
# import yaml

# nest_asyncio.apply()

# config_path=r'..\config\config.yaml'
# provinces = ["Ontario", "British Columbia", "Alberta", "Quebec", "Manitoba", "Saskatchewan", "Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island", "Northwest Territories", "Nunavut", "Yukon"]
# province_facts = {}
# CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
# KEYS = yaml.safe_load(open(CONFIG["KEYS"], 'r', encoding='utf-8'))
# OPENAI_API_KEY = KEYS["OPENAI_API_KEY"]

# results = []
# results_dict = {}

# def get_tasks(session):
#     """Get the tasks"""
#     tasks = []
#     _headers = {"Content-Type": "application/json", "Authorization": f"Bearer {OPENAI_API_KEY}"}
#     for province_name in provinces:
#         print(f"\nGetting facts for: {province_name}")
#         payload = {
#             "model": "gpt-3.5-turbo",
#             "temperature": 0,
#             "max_tokens": 200,
#             "messages": [
#                 {"role": "system", "content": "You are an expert in Canadian history."},
#                 {"role": "user", "content": f"What year was {province_name} named the current name (as of last information cut-off date)?"},
#                 {"role": "system", "content": "Please keep your answer short and to the point."}
#             ]
#         }
#         tasks.append(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
#     return tasks

# async def province_year():
#     """Get the year a province was founded"""
#     async with aiohttp.ClientSession() as session:
#         tasks = get_tasks(session)
#         # print(tasks)
#         responses = await asyncio.gather(*tasks)
#         for response in responses:
#             response = await response.json()
#             if 'choices' in response:
#                 # await print(response['choices'][0]['message']['content'])
#                 results.append(response['choices'][0]['message']['content'])
#     return results

# async def main():
#     # start_user()
#     facts = await province_year()
#     print(f"\nHere are the facts about Provinces: {facts}")
#     # for k, v in facts.items():
#     #     print(f"\nProvince: {k}\n Fact: {v}")

# if __name__ == "__main__":
#     time_start = time.perf_counter()
#     asyncio.run(main())
#     elapsed = time.perf_counter() - time_start
#     print(f"Time elapsed: {elapsed:0.2f} seconds")