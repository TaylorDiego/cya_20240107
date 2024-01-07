"""AI Question Checker"""

import time
import asyncio
import nest_asyncio
import aiohttp
import json
import yaml

nest_asyncio.apply()

class QuestionEvaluator():
    def __init__(self) -> None:
        """Initialize the class"""
        self.config_path = r'..\config\config.yaml'
        self.question_checks = {}
        self.kb_articles = ["subjects\\ODX\\categories\\ODX\\MUST_What_is_an_ODX_Server__context.json"]

        self.CONFIG = yaml.safe_load(open(self.config_path, 'r', encoding='utf-8'))
        self.STORE_1 = self.CONFIG["STORE_1"]
        self.STORE_2 = self.CONFIG["STORE_2"]
        self.STORE_3 = self.CONFIG["STORE_3"]

        self.KEYS = yaml.safe_load(open(self.CONFIG["KEYS"], 'r', encoding='utf-8'))
        self.OPENAI_API_KEY = self.KEYS["OPENAI_API_KEY"]

        self.questions_fast = {
            "typos": {
                "role_content": "You are a powerful teaching assistant, responsible for reviewing new test questions.",
                "user_content_template": "Please review the question for any typos, and make a list of the misspelled items, and how to fix each one. Keep your repsonse in plain English format."
            }
            , "grammar": {
                "role_content": "You are a powerful teaching assistant, responsible for reviewing new test questions.",
                "user_content_template": "Please review the question for any grammatical issues, considering the diversity of question readers (in its final format). Keep your repsonse in plain English format."
            }
        }
        self.questions_details = {
            "relevance": {
                "role_content": "You are a powerful teaching assistant, responsible for reviewing new test questions.",
                "user_content_template": "Please review the question and the original material, to ensure that the questions are RELEVANT to the material. Keep your repsonse in plain English format."
            }
            , "truth": {
                "role_content": "You are a powerful teaching assistant, responsible for reviewing new test questions.",
                "user_content_template": "Please review the answers to the question, to ensure that the answers are TRUE. Keep your repsonse in plain English format."
            }
            , "bs": {
                "role_content": "You are a powerful teaching assistant, responsible for reviewing new test questions.",
                "user_content_template": "Please review the questions and answers, to ensure that the questions and answers are not 'BS', meaning bullshit. A 'bullshit' question can be a 'trick question', a 'gotcha question', or any kind of question that may be frustrating to a test taker, for any reason. Imagine you are a bit stressed out human test-taker, and consider how the question would be considered either 'good' or 'BS'. Keep your repsonse in plain English format."
            }
            , "improvement": {
                "role_content": "You are a powerful teaching assistant, responsible for reviewing new test questions.",
                "user_content_template": "Please be very harsh and critical to suggest some improvements to the question. Do not revise the question; only highlight what may be problematic. (This will help the user rank the questions, later.) Keep your repsonse in plain English format."
            }
            , "overall": {
                "role_content": "You are a powerful teaching assistant, responsible for reviewing new test questions.",
                "user_content_template": "Please give an overall 'rating' of the question, from 1 to 5, where 1 is 'very bad question', 3 is 'okay question' and 5 is 'very good question'. Keep your repsonse in plain English format."
            }
        }

    async def build_payload_fast(self, role_content, user_content, question, kb_article):
        """Build the payload"""
        payload = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,
            "max_tokens": 200,
            "messages": [
                {"role": "system", "content": role_content},
                {"role": "user", "content": user_content},
                {"role": "system", "content": f"Question to review: {question}"},
                {"role": "system", "content": f"Article (webscrape kb content) to judge the question: {kb_article}"},
                {"role": "system", "content": "Please keep your answer short and to the point."}
            ]
        }
        return payload
    
    async def build_payload_details(self, role_content, user_content, question, kb_article):
        """Build the payloade""" # "gpt-3.5-turbo", "gpt-3.5-turbo-1106" "gpt-4", "gpt-4-1106-preview"
        payload = {
            "model": "gpt-3.5-turbo"
            , "temperature": 0.8
            , "max_tokens": 500
            , "messages": [
                {"role": "system", "content": role_content},
                {"role": "user", "content": user_content},
                {"role": "system", "content": f"Question to review: {question}"},
                {"role": "system", "content": f"Article (webscrape kb content) to judge the question: {kb_article}"},
                {"role": "system", "content": "Please keep your answer short and to the point."}
            ]
        }
        return payload

    async def read_article(self, kb_article_path):
        """Get the article"""
        with open(f"{self.STORE_1}\\{kb_article_path}", 'r', encoding='utf-8') as file:
            article = json.load(file)
        return article

    async def read_quiz(self, quiz_path):
        """Get the question"""
        with open(f"{self.STORE_2}\\{quiz_path}", 'r', encoding='utf-8') as file:
            quiz = json.load(file)
        return quiz

    async def get_tasks(self, session):
        """Get the tasks"""
        tasks = []
        _headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.OPENAI_API_KEY}"}
        for _a in self.kb_articles:
            article = await self.read_article(_a)
            print(_a)
            _quiz_path = _a.replace("context", "quiz_raw").replace(self.STORE_1, self.STORE_2)
            _quiz = await self.read_quiz(_quiz_path)
            for _question_num, _question_content in _quiz.items():
                for question_type, question_info in self.questions_fast.items():
                    payload = await self.build_payload_fast(
                        question_info["role_content"], 
                        question_info["user_content_template"].format(_question_content),
                        _question_content,
                        article
                    )
                    task = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
                    tasks.append((_quiz_path, _question_num, article, _question_content, question_type, task))
                
                for question_type, question_info in self.questions_details.items():
                    payload = await self.build_payload_details(
                        question_info["role_content"], 
                        question_info["user_content_template"].format(_question_content),
                        _question_content,
                        article
                    )
                    task = asyncio.ensure_future(session.post("https://api.openai.com/v1/chat/completions", json=payload, headers=_headers, ssl=False))
                    tasks.append((_quiz_path, _question_num, article, _question_content, question_type, task))
        return tasks

    async def save_output(self, question_checks, file_path):
        """Save the output to a file"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(question_checks, file, ensure_ascii=False, indent=4)

    async def main(self):
        """Run the main program"""
        async with aiohttp.ClientSession() as session:
            tasks = await self.get_tasks(session)
            responses = await asyncio.gather(*(task for _, _, _, _, _, task in tasks))
            for (_quiz_path, question_file, article_item, question_item, fact_type, _), response in zip(tasks, responses):
                response = await response.json()
                if 'choices' in response:
                    if question_file not in self.question_checks:
                        self.question_checks[question_file] = []
                    fact = response['choices'][0]['message']['content']
                    self.question_checks[question_file].append(fact)

            # Generate the output file path outside of the loop
            output_file_path = self.STORE_3 + "\\"+ _quiz_path.replace("quiz_raw", "quiz_eval")

            # Then, inside the loop, you can simply use this path to save the output
            for k, v in self.question_checks.items():
                print(f"Saving output to {output_file_path}")
                await self.save_output(v, output_file_path)
        return self.question_checks

    # async def main(self):
    #     """Run the main program"""
    #     async with aiohttp.ClientSession() as session:
    #         tasks = await self.get_tasks(session)
    #         responses = await asyncio.gather(*(task for _, _, _, _, _, task in tasks))
    #         for (_quiz_path, question_file, article_item, question_item, fact_type, _), response in zip(tasks, responses):
    #             response = await response.json()
    #             if 'choices' in response:
    #                 if question_file not in self.question_checks:
    #                     self.question_checks[question_file] = []
    #                 fact = response['choices'][0]['message']['content']
    #                 self.question_checks[question_file].append(fact)
    #         # After the question_checks dictionary has been populated:
    #         for k, v in self.question_checks.items():
    #             output_file_path = _quiz_path.replace(self.STORE_2, self.STORE_3).replace("quiz_raw", "quiz_eval")
    #             print(f"Saving output to {output_file_path}")
    #             await self.save_output(v, output_file_path)
    #     return self.question_checks

if __name__ == "__main__":
    time_start = time.perf_counter()
    facts = QuestionEvaluator()
    question_checks = asyncio.run(facts.main())
    elapsed = time.perf_counter() - time_start

    print("\nHere are the facts about Questions:")
    print(f"\n{question_checks}\n\n")

    # for k, v in question_checks.items():
    #     print(f"\nQuestion: {k}")
    #     for fact in v:
    #         print(f"Fact: {fact}")

    print(f"\n\nPERFORMANCE: Time elapsed: {elapsed:0.2f} seconds")