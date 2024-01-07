"""This script will collect the first question from each quiz and save it to a file, by subject/type."""

import json
import os
import yaml

class CollectTopQuestions:
    def __init__(self, config_path=r'..\config\config.yaml'):
        # self._folder = "" # _folder
        # self._category = "" # _category
        self.CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.FOLDERS = self.CONFIG["FOLDERS"]
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_2 = self.CONFIG["STORE_2"]
        self.STORE_5 = self.CONFIG["STORE_5"]
        self.USER_CHECK = self.CONFIG["USER_CHECK"]
        self.TESTINVITE = self.CONFIG["TESTINVITE"]

    def read_json(self, file_path):
        """Read a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
        
    def save_json(self, file_path, content):
        """Save a JSON file"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(content, file, ensure_ascii=False, indent=4)

    def clean_dict(self, _dict):
        """Remove empty values from a dictionary"""
        _clean_dict = {k: v for k, v in _dict.items() if v}
        return _clean_dict

    def get_articles(self, _file_type='__context.json'):
        """make a dict from the json files in the content store: STORE_1"""
        _cs_path = self.STORE_2
        dir_dict = {}
        for root, dirs, files in os.walk(_cs_path):
            # print("\nroot: ", root)
            # print("dirs", dirs)
            # print("files", files)
            if files:  # Check if there are any files in the directory
                dir_dict[root] = [file for file in files if file.endswith(_file_type)]
                c_dir_dict = self.clean_dict(dir_dict)
                # print(c_dir_dict)
        return c_dir_dict
    

    def collect_first_n_questions(self, n=1):
        """for each quiz, collect the first n questions"""
        quiz_dict = {}
        c_dir_dict = self.get_articles()
        _count_context = 0
        for folder, files in c_dir_dict.items():
            for file in files:
                file_path = os.path.join(folder, file)
                if "__context" in file_path:
                    _count_context += 1
                    continue
                print(file_path)
                quiz = self.read_json(file_path)
                if "\MUST_" in file_path:
                    print("MUST_ gets two questions")
                elif "\SHOULD_" in file_path:
                    print("SHOULD_ gets two questions")
                elif "\COULD_" in file_path:
                    print("COULD_ gets one question")
                else:
                    print("No prefix")
                # print(quiz)
        #         quiz_dict[file] = ""
        print(_count_context)
        # return quiz_dict

    # def collect_first_q(self, folder, category, quiz):
    #     """Collect the first question from each quiz"""
    #     _folder = folder
    #     _category = category
    #     _question = quiz["question"]
    #     _answer = quiz["answer"]
    #     _options = quiz["options"]
    #     _first_q = {
    #         "folder": _folder,
    #         "category": _category,
    #         "question": _question,
    #         "answer": _answer,
    #         "options": _options
    #     }
    #     print(_first_q)
    #     return _first_q

    def main(self):
        self.collect_first_n_questions()

if __name__ == "__main__":
    collect_first_q = CollectTopQuestions()
    collect_first_q.main()