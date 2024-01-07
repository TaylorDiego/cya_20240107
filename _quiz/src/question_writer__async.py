"""This script loads a context file and creates an AI output (quiz)."""

import os, sys
import time
import json
import asyncio
import aiofiles
from openai import OpenAI
import shutil
import pandas as pd
import aiohttp
import yaml

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

class BaseQuizWriter:
    """Base quiz writer class"""
    def __init__(self, config_path=r'..\config\config.yaml'):
        self.CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.TASK = self.CONFIG["TASK"]
        self.TASK_FORMAT = self.CONFIG["TASK_FORMAT"]

        self.KEYS = yaml.safe_load(open(self.CONFIG["KEYS"], 'r', encoding='utf-8'))
        self.OPENAI_API_KEY = self.KEYS["OPENAI_API_KEY"]

        self.question_types = (
            {
            "(TF) True/False": "Simple True or False questions, with a single correct answer."
            , "(MC) Multiple choice": "Multiple Choice (a, b, c, d) questions, with a single correct answer."
            , "(FB) Fill-in-the-blank": "The question is formatted as a complete, and TRUE sentence with a single word ommitted. There should be four (a, b, c, d) possible answers, and only one correct answer. Each option MUST BE A SINGLE WORD."
            }
        )
        self.question_types = ({
            "MUST": {
                "make_6_MC": {
                    "q_format": "MC"
                    , "q_count": "six (6)"
                    , "q_type": "conceptual"
                    , "focus": "key points in the context" # revisit this when more complex chekcing logic
                }
            }
            , "SHOULD": {
                "make_4_MC": {
                    "q_format": "MC"
                    , "q_count": "four (4)"
                    , "q_type": "basic"
                    , "focus": "key points in the context" # revisit this when more complex chekcing logic
                }
            }
            , "COULD": {
                "make_2_MC": {
                    "q_format": "MC"
                    , "q_count": "two (2)"
                    , "q_type": "basic"
                    , "focus": "key points in the context" # revisit this when more complex chekcing logic
                }
            }
            , "WON'T": {
                "make_0_MC": {
                    "q_format": "MC"
                    , "q_count":  "ZERO (0); simply say to USER: 'article type listed as WON'T means that this article is excluded!' "
                    , "q_type":  "none"
                    , "focus": "none"
                }
            }
        })

    def read_file(self, file_path):
        """Read a file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    async def write_questions(self, q_format, q_count, q_type, focus, context, add_context="missing"):
        """Make the questions"""
        if len(context) == 0:
            raise ValueError("Error: Context (file) is empty. Please check the file, see config.yaml.")
        else:
            format_json = self.read_file(self.TASK_FORMAT)
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": "gpt-4-1106-preview"
                    , "temperature": 0
                    , "messages": [
                        {
                            "role": "system" # describe the agent's role
                            , "content": "You are an expert educator and quiz maker."
                        }
                        , {
                            "role": "system" # types of questions
                            , "content": f"The user will ask you to make a particular kind of question, or set of questions, from a given text. Make sure to include the question, the answer, and a complete explanation. The user may use short-hand in their request, using this 'legend': {self.question_types}"
                        }
                        , {
                            "role": "system" # conceptual vs practical
                            , "content": "The user may request a level of abstraction (a 'continuum' ranging from Practical & Applicable to Conceptual & Use Case focused). With this difficulty level indicated, we then need to change the level of exmplanation. For practical questions, there should be a short, complete sentence in the explanation. When the questions are conceptual, the explanation needs to be very clear for all learners to pass the scrutiny of all, in 2-3 sentences, at most, please. "
                        }
                        , {
                            "role": "user" # number of questions, focus of the questions, and any additional context
                            , "content": f"Please make {q_count} {q_format} questions, with a particular focus on {focus} and relative abstraction {q_type} from Conceptual to Practical, using the following contextual information: << {context} >>, and additional context , if any, : << {add_context} >>"
                        }
                        , {
                            "role": "system" # the output formatted in json
                            , "content": f"Please ensure that the output of each question is in correct, proper JSON format, specifically like this: {format_json}. That means that you should not 'say anything' only to provide the JSON response. For example, do NOT put three ''' marks around the JSON, or any other text, for that matter; just provide the JSON, and nothing else."
                        }
                    ]
                    }
                _headers = {"Authorization": f"Bearer {self.OPENAI_API_KEY}"}
                result = None
                async with session.post("https://api.openai.com/v1/engines/gpt-4-1106-preview/completions", 
                                        headers=_headers, 
                                        data=json.dumps(payload)) as response:
                    if response.status == 200:
                        data = await response.json()

                        if asyncio.iscoroutine(data.message.content):
                            result = await data.choices[0].message.content
                        else:
                            result = data.choices[0].message.content
                return result

    # def clear_file(self, file_path):
    #     filename = self.TASK
    #     with open(filename, 'w', encoding='utf-8') as file:
    #         file.close()

    # async def save_quiz(self, filename, _content):
    #     """Write to a file"""
    #     _content = await _content
    #     with open(filename, 'w+', encoding='utf-8') as file:
    #         if isinstance(_content, str):
    #             file.write(_content)
    #         else:
    #             json.dump(_content, file, indent=4)

    def parse_filename(self, file_name):
        """Parse the filename to get the subject, category, and type."""
        _filename = file_name.split('_')
        article_type = _filename[0]
        return article_type

    def get_question_params(self, file_name):
        """Get the question parameters from the title of the context file, which is admittedly a bit hacky."""
        _article_type = self.parse_filename(file_name)
        # print(f'\nArticle type: {_article_type}')
        _question_param_dict = self.question_types[_article_type] # determines types of questions (see above)
        return _question_param_dict

    async def clean_response(self, response):
        if asyncio.iscoroutine(response):
            response = await response
        if response is not None:
            rm_newlines = response.replace('\n', '').replace('\\', '').replace('```json', '').replace('```', '')
        else:
            rm_newlines = None
        # rm_newlines = response.replace('\n', '').replace('\\', '').replace('```json', '').replace('```', '')
        return rm_newlines

    async def run_question_maker(self, _folder, _file_name):
        _path = f'{_folder}\\{_file_name}'
        context = self.read_file(_path)
        # print(f'\nContext: {context}')
        _question_params = self.get_question_params(_file_name)
        # _questions = []
        for k, q_params in _question_params.items():
            q_format = q_params["q_format"]
            q_count = q_params["q_count"]
            q_type = q_params["q_type"]
            focus = q_params["focus"]
            await asyncio.sleep(1)
            print(f'\nAI AGENT: I will write {q_count} {q_format}, {q_type} questions with a focus on {focus} for this article context.')
            response = await self.write_questions(q_format, q_count, q_type, focus, context, add_context="missing")
            c_response = self.clean_response(response)
            print(f'\n{c_response}')
        return c_response

    async def main(self, _folder, _file_name):
        """Main function"""
        task = self.TASK
        # self.clear_file(task) # was used when appending to the file, but now just overwriting it, so this isn't needed
        _questions = await self.run_question_maker(_folder, _file_name)
        # self.save_quiz(task, _questions)
        return _questions

class UserWriter:
    """User writer class"""
    def __init__(self):
        """Initialize the class"""
        self.CONFIG = yaml.safe_load(open(r'..\config\config.yaml', 'r', encoding='utf-8'))
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_1 = self.CONFIG["STORE_1"]
        self.STORE_2 = self.CONFIG["STORE_2"]

    def user_input(self):
        """Get user input"""
        q_format = input("\ nChoose a question FORMAT: \n")
        q_count = input("\nChoose a question COUNT: \n")
        q_type = input("\nChoose question PURPOSE: more PRACTICAL or more CONCEPTUAL: \n")
        focus = input("\nChoose a few words to FOCUS on as the topic for the question(s): \n")
        return q_format, q_count, q_type, focus

    def main(self):
        print("\nUser Writer (process initiated)...")

class BulkWriter:
    """Bulk writer class"""
    def __init__(self) -> None:
        self.CONFIG = yaml.safe_load(open(r'..\config\config.yaml', 'r', encoding='utf-8'))
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_1 = self.CONFIG["STORE_1"]
        self.STORE_2 = self.CONFIG["STORE_2"]
        self.TASK = self.CONFIG["TASK"]

        self.STORE_1_TEST = self.CONFIG["STORE_1_TEST"]
        self.STORE_2_TEST = self.CONFIG["STORE_2_TEST"]

    def select_cs_input(self):
        """Select the dir to get context file(s)"""
        _test_cs = self.STORE_1_TEST
        _main_cs = self.STORE_1
        _default = _main_cs
        print(f'You selected BULK MODE. Use the default {_default} or select a different path.')
        _choice = input("\nUse default path? \na: yes \nb: no\n\nPlease enter a or b: ")

        if _choice.strip().lower() == 'a':
            print("\nGreat! You selected the default content store.")
            _path = _default
            return _path
        
        elif _default.strip().lower() == 'b':
            print("\nGreat! You selected a different path.")
            _path = input("\nEnter the path to the context file: ")
            return _path

    def load_cs_dir(self, _path, _file_type='__context.json'):
        """Read content store dir, and make a dict of the files"""
        _cs_path = self.STORE_1
        dir_dict = {}
        for root, dirs, files in os.walk(_cs_path):
            if files:  # Check if there are any files in the directory
                dir_dict[root] = [file for file in files if file.endswith(_file_type)]
        return dir_dict

    async def save_quiz(self, filename, _content):
        """Write to a file"""
        _content = await _content
        with open(filename, 'w+', encoding='utf-8') as file:
            if isinstance(_content, str):
                file.write(_content)
            else:
                json.dump(_content, file, indent=4)

    async def save_to_store(self, _folder, _file, _content):
        """Save the raw quiz file to the content store"""
        folder = _folder.replace(self.STORE_1, self.STORE_2)
        filename = _file.replace('__context.json', '__quiz_raw.json')
        _path = f'{folder}\\{filename}'
        print(f'\nSaving to: {_path}')
        _content = await _content
        async with aiofiles.open(_path, mode='w') as f:
            if _content is not None:
               await f.write(_content)
            else:
                print(f'\nNo content to write to file: {_path}')
        # shutil.copy(self.TASK, _path)

    def count_nested_values(self, _dir_dict):
        return sum(len(_f) for _f in _dir_dict.values())
    
    # def check_if_exists(self, _folder, _file_name):
    #     """Check if file exists in the content store already"""
    #     _path = f'{_folder}\\{_file_name}'
    #     if os.path.exists(_path):
    #         return True
    #     else:
    #         return False

    async def process_file(self, question_maker, _folder, _file):
        """Process a single file"""
        _questions = await question_maker.main(_folder, _file)
        await self.save_to_store(_folder, _file, _questions)

    async def run_bulk_writer(self, _dir_dict):
        """Run the bulk writer"""
        _dict = _dir_dict
        _total_files = self.count_nested_values(_dict)
        _idx = 1
        tasks = []  # Create a list to hold all tasks
        for _folder, _f in _dict.items():
            for _file in _f:
                print(f'\nWorking on file {_idx} of {_total_files} total files...')
                print(f'\nfile: {_file}')
                _idx += 1
                question_maker = BaseQuizWriter()
                try:
                    # Create a task for each file and add it to the tasks list
                    task = asyncio.ensure_future(self.process_file(question_maker, _folder, _file))
                    tasks.append(task)
                except Exception as e:
                    print(f"An error occurred while processing the file {_file}: {e}")
        results = await asyncio.gather(*tasks)
        return results

    # async def run_bulk_writer(self, _dir_dict):
    #     """Run the bulk writer"""
    #     _dict = _dir_dict
    #     _total_files = self.count_nested_values(_dict)
    #     _idx = 1
    #     _time_start = time.time()
    #     for _folder, _f in _dict.items():
    #         # print(f'\nfolder: {_folder}')

    #         for _file in _f:
    #             # _check = self.check_if_exists(_folder, _file)
    #             # if _check:
    #             #     print(f'\nSkipping file {_idx} of {_total_files} total files...')
    #             #     print(f'\nfile: {_file}')
    #             #     _idx += 1
    #             #     continue
    #             print(f'\nWorking on file {_idx} of {_total_files} total files...')
    #             print(f'\nfile: {_file}')
    #             _idx += 1
    #             _sleep = 0.5
    #             await asyncio.sleep(_sleep)
    #             question_maker = BaseQuizWriter()
    #             _questions = await question_maker.main(_folder, _file)
    #             await self.save_to_store(_folder, _file, _questions)
    #     _time_end = time.time()
    #     _time_used_seconds = _time_end - _time_start - (_total_files * _sleep) # subtract the time.sleep() from the total time
    #     print(f'\nTotal time: {_time_used_seconds} seconds!')

    async def main(self):
        """Main function"""
        print("\nBulk Writer (process initiated)...")
        _path = self.select_cs_input()
        _dir_dict = self.load_cs_dir(_path)
        await self.run_bulk_writer(_dir_dict)

class WriterSelector:
    """Writer selector class"""
    def __init__(self) -> None:
        self.CONFIG = yaml.safe_load(open(r'..\config\config.yaml', 'r', encoding='utf-8'))
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_1 = self.CONFIG["STORE_1"]
        self.STORE_2 = self.CONFIG["STORE_2"]

    async def start_user(self):
        _writer = input("\nSelect your method: \n\na: directory (BULK MODE) \nb: single file (USER MODE)\n\nPlease enter a or b: ")

        if _writer.strip().lower() == 'a':
            print("\nselected: BULK MODE...")
            bulk_writer = BulkWriter()
            await bulk_writer.main()

        elif _writer.strip().lower() == 'b':
            print("\nselected: USER MODE...")
            user_writer = UserWriter()
            await user_writer.main()

        else:
            print("\nInvalid option. Please try again.")

    async def main(self):
        await self.start_user()


if __name__ == "__main__":
    writer_selector = WriterSelector()
    asyncio.run(writer_selector.main())

    # _folder = "..\\\\CONTENT_STORE\\\\_cs_1_context\\subjects\\Data Warehouse\\categories\\Data Warehouse"
    # _file_name = "MUST_Table_relations__context.json"
    # question_maker = BaseQuizWriter()
    # question_maker.main(_folder, _file_name)
