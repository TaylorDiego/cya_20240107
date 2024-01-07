"""Example of using OpenAI to get facts about provinces, using requests"""

import time
import asyncio
import nest_asyncio
import aiohttp
import yaml

nest_asyncio.apply()

class ProvinceFacts():
    def __init__(self) -> None:
        """Initialize the class"""
        self.config_path = r'..\config\config.yaml'
        self.provinces = ["Ontario", "British Columbia", "Alberta", "Quebec", "Manitoba", "Saskatchewan","Nova Scotia", "New Brunswick", "Newfoundland and Labrador", "Prince Edward Island","Northwest Territories", "Nunavut", "Yukon"]
        self.province_facts = {}
        self.CONFIG = yaml.safe_load(open(self.config_path, 'r', encoding='utf-8'))
        self.KEYS = yaml.safe_load(open(self.CONFIG["KEYS"], 'r', encoding='utf-8'))
        self.OPENAI_API_KEY = self.KEYS["OPENAI_API_KEY"]
        self.prompts_main = {
            "weather": {
                "messages": [
                    {"system": "You are an expert in Canadian weather."}
                    , {"user": "What is the weather like in {PROVINCE_NAME}? But, explain it like you are talking to an old friend, with no meteorological jargon."}
                    , {"user": "For example, tell me if it is hot or cold in {PROVINCE_NAME}, and if it is sunny or rainy. Tell me when the snow, if any falls, and how much snow falls. Tell me if there are any storms, and if so, what kind of storms."}
                    , {"system": "Please keep your answer short and to the point."}
                ]
            }
        }
        self.questions_fast = {
            "year": {
                "role_content": "You are an expert in Canadian history.",
                "user_content_template": "What year was {} named the current name (as of last information cut-off date)?"
            }
            , "population": {
                "role_content": "You are an expert in Canadian demographics.",
                "user_content_template": "What is the population of {}?"
            }
            , "income": {
                "role_content": "You are an expert in Canadian demographics.",
                "user_content_template": "What is the average salary (per household) {}?"
            }
            , "languages": {
                "role_content": "You are an expert in Canadian demographics.",
                "user_content_template": "What are the main languages spoken in {}?"
            }
            , "capital": {
                "role_content": "You are an expert in Canadian geography.",
                "user_content_template": "What is the capital of {}?"
            }
        }
        self.questions_details = {
            "history": {
                "role_content": "You are an expert in Canadian history.",
                "user_content_template": "What is the history of {}?"
            }
            , "industries": {
                "role_content": "You are an expert in Canadian business.",
                "user_content_template": "What are the main industries in {}?"
            }
            , "companies": {
                "role_content": "You are an expert in Canadian business.",
                "user_content_template": "What are the most famous companies in {}?"
            }
        }

    async def build_payload_main(self, _prompts_main_item, province_name):
        """Build the payload for a province"""
        messages = []
        placeholder = "{PROVINCE_NAME}"
        print(province_name)
        for _message_line in _prompts_main_item["messages"]:
            # print(_message_line)
            if placeholder in _message_line:
                print("FOUND!)")
                _message_line.replace(placeholder, province_name)
                messages.append(_message_line)
            else:
                print("NOT FOUND!)")
        # print(messages)
        payload = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,
            "max_tokens": 200,
            "messages": messages
        }
        return payload


    # async def build_payload_fast(self, role_content, user_content):
    #     """Build the payload for a province"""
    #     payload = {
    #         "model": "gpt-3.5-turbo",
    #         "temperature": 0.1,
    #         "max_tokens": 200,
    #         "messages": [
    #             {"role": "system", "content": role_content},
    #             {"role": "user", "content": user_content},
    #             {"role": "system", "content": "Please keep your answer short and to the point."}
    #         ]
    #     }
    #     return payload
    
    # async def build_payload_details(self, role_content, user_content):
    #     """Build the payload for a province""" # "gpt-3.5-turbo", "gpt-3.5-turbo-1106" "gpt-4", "gpt-4-1106-preview"
    #     payload = {
    #         "model": "gpt-3.5-turbo"
    #         , "temperature": 0.1
    #         , "max_tokens": 500
    #         , "messages": [
    #             {"role": "system", "content": role_content},
    #             {"role": "user", "content": user_content},
    #             {"role": "system", "content": "Please keep your answer short and to the point."}
    #         ]
    #     }
    #     return payload



    # async def get_tasks(self, session):
    #     """Get the tasks"""
    #     tasks = []
    #     _headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.OPENAI_API_KEY}"}
    #     for province_name in self.provinces:
    #         print(province_name)
    #         for _topic, _prompt in self.prompts_main.items():
    #             for _message in _prompt["messages"]:
    #                 # print(_message)
    #                 if "content" in _message:
    #                     _message["content"] = _message["content"].format(province_name)
    #             payload = await self.build_payload_main(
    #                 _prompt["messages"]
    #             )
    #             # payload = await self.build_payload_main(
    #             #     _prompt["messages"].format(province_name)
    #             # )
    #             print(payload)
    #             task = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
    #             tasks.append((province_name, _topic, task))

    #         # for question_type, question_info in self.questions_fast.items():
    #         #     payload = await self.build_payload_fast(
    #         #         question_info["role_content"], 
    #         #         question_info["user_content_template"].format(province_name)
    #         #     )
    #         #     task = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
    #         #     tasks.append((province_name, question_type, task))

    #         # for question_type, question_info in self.questions_details.items():
    #         #     payload = await self.build_payload_details(
    #         #         question_info["role_content"], 
    #         #         question_info["user_content_template"].format(province_name)
    #         #     )
    #         #     task = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
    #         #     tasks.append((province_name, question_type, task))
    #     return tasks

    async def main(self):
        """Run the main program"""
        # nest_asyncio.apply()
        for province_name in self.provinces:
            # print(province_name)

            for _prompt in self.prompts_main.items():
                # print(_prompt)
                self.build_payload_main(_prompt, province_name)
        # async with aiohttp.ClientSession() as session:
        #     tasks = await self.get_tasks(session)
        #     responses = await asyncio.gather(*(task for _, _, task in tasks))
        #     for (province_name, fact_type, _), response in zip(tasks, responses):
        #         response = await response.json()
        #         if 'choices' in response:
        #             if province_name not in self.province_facts:
        #                 self.province_facts[province_name] = {}
        #             self.province_facts[province_name][fact_type] = response['choices'][0]['message']['content']
        # return self.province_facts

if __name__ == "__main__":
    facts = ProvinceFacts()
    facts.main()

    # time_start = time.perf_counter()
    # facts = ProvinceFacts()
    # province_facts = asyncio.run(facts.main())
    # elapsed = time.perf_counter() - time_start

    # print("\nHere are the facts about Provinces:")
    # for k, v in province_facts.items():
    #     print(f"\nProvince: {k}")
    #     for v2 in v.values():
    #         print(f"fact: {v2}")

    # print(f"\n\nPERFORMANCE: Time elapsed: {elapsed:0.2f} seconds")