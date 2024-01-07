"""Example of using OpenAI to get facts about provinces, using requests"""

import time
import asyncio
import nest_asyncio
import aiohttp
import yaml

class ProvinceFacts():
    def __init__(self) -> None:
        """Initialize the class"""
        self.config_path = r'..\config\config.yaml'
        self.provinces = ["Ontario", "British Columbia", "Alberta", "Quebec", "Manitoba", "Saskatchewan","Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island","Northwest Territories", "Nunavut", "Yukon"]
        self.province_facts = {}
        self.CONFIG = yaml.safe_load(open(self.config_path, 'r', encoding='utf-8'))
        self.KEYS = yaml.safe_load(open(self.CONFIG["KEYS"], 'r', encoding='utf-8'))
        self.OPENAI_API_KEY = self.KEYS["OPENAI_API_KEY"]


    async def build_payload_year(self, province_name):
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

    async def build_payload_population(self, province_name):
        """Build the payload for a province's population"""
        payload = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "max_tokens": 200,
            "messages": [
                {"role": "system", "content": "You are an expert in Canadian demographics."},
                {"role": "user", "content": f"What is the population of {province_name} (as of last information cut-off date)?"},
                {"role": "system", "content": "Please keep your answer short and to the point."}
            ]
        }
        return payload
    
    async def build_payload_income(self, province_name):
        """Build the payload for a province's population"""
        payload = {
            "model": "gpt-3.5-turbo",
            "temperature": 0,
            "max_tokens": 200,
            "messages": [
                {"role": "system", "content": "You are an expert in Canadian demographics."},
                {"role": "user", "content": f"What is the average salary (per household) {province_name} (as of last information cut-off date)?"},
                {"role": "system", "content": "Please keep your answer short and to the point."}
            ]
        }
        return payload

    async def get_tasks(self, session):
        """Get the tasks"""
        tasks = []
        _headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.OPENAI_API_KEY}"}
        for province_name in self.provinces:
            payload_year = await self.build_payload_year(province_name)
            task_year = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload_year, headers=_headers, ssl=False))
            tasks.append((province_name, "year", task_year))

            payload_population = await self.build_payload_population(province_name)
            task_population = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload_population, headers=_headers, ssl=False))
            tasks.append((province_name, "population", task_population))

            payload_income = await self.build_payload_income(province_name)
            task_income= asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload_income, headers=_headers, ssl=False))
            tasks.append((province_name, "income", task_income))
        return tasks

    async def main(self):
        """Run the main program"""
        async with aiohttp.ClientSession() as session:
            tasks = await self.get_tasks(session)
            responses = await asyncio.gather(*(task for _, _, task in tasks))
            for (province_name, fact_type, _), response in zip(tasks, responses):
                response = await response.json()
                if 'choices' in response:
                    if province_name not in self.province_facts:
                        self.province_facts[province_name] = {}
                    self.province_facts[province_name][fact_type] = response['choices'][0]['message']['content']
        return self.province_facts

if __name__ == "__main__":
    nest_asyncio.apply()
    time_start = time.perf_counter()
    facts = ProvinceFacts()
    province_facts = asyncio.run(facts.main())
    elapsed = time.perf_counter() - time_start

    print("\nHere are the facts about Provinces:")
    # print(province_facts)

    for k, v in province_facts.items():
        print(f"\nProvince: {k}")
        for v2 in v.values():
            print(f"fact: {v2}")

    print(f"\n\nPERFORMANCE: Time elapsed: {elapsed:0.2f} seconds")