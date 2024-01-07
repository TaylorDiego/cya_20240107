"""This script formats questions to be uploaded as bulk questions to TestInvite."""

import json
import yaml

class UploadFormatter:
    def __init__(self, config_path=r'..\config\config.yaml'):
        # self._folder = "" # _folder
        # self._category = "" # _category
        self.CONFIG = yaml.safe_load(open(config_path, 'r', encoding='utf-8'))
        self.FOLDERS = self.CONFIG["FOLDERS"]
        self.CONTEXT = self.CONFIG["CONTEXT"]
        self.STORE_5 = self.CONFIG["STORE_5"]
        self.USER_CHECK = self.CONFIG["USER_CHECK"]
        self.TESTINVITE = self.CONFIG["TESTINVITE"]


    def read_json(self, file_path):
        """Read a JSON file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)

    def make_quiz_format_head(self, folder, category, quiz, shuffle=True, direction="column"):
        """Make the quiz format for the header"""
        _folder = f'"folder":"{folder}"'
        _tags = ',"tags":{'+ f'"category":"{category}"'+ '}'
        _shuffle = f'"shuffle":{str(shuffle).lower()}'
        _block = f',"points":[1,0], "min":1, "max":1, {_shuffle}, "display":{{"direction":"{direction}"}}'
        _question = quiz["question"]
        c_format = '{' + ''.join([_folder,_tags,_block]) + '}' + f'{_question}'
        return c_format

    def make_quiz_format_scores(self, quiz, num_correct_options):
        """Make the quiz format for the scores"""
        options = {
            "option_a": {"percent": 0, "text": quiz['options']["option_a"]},
            "option_b": {"percent": 0, "text": quiz['options']["option_b"]},
            "option_c": {"percent": 0, "text": quiz['options']["option_c"]},
            "option_d": {"percent": 0, "text": quiz['options']["option_d"]}
        }

        _answer = quiz["answer"]

        if _answer is not None:
            # print(_answer)
            options[_answer]["percent"] = float(100/num_correct_options)
            # print(options[_answer]["percent"])

        _opt_a_score = options["option_a"]["percent"]
        _opt_b_score = options["option_b"]["percent"]
        _opt_c_score = options["option_c"]["percent"]
        _opt_d_score = options["option_d"]["percent"]

        _format = (f'{{"score":{_opt_a_score}}}{options["option_a"]["text"]}\n{{"score":{_opt_b_score}}}{options["option_b"]["text"]}\n{{"score":{_opt_c_score}}}{options["option_c"]["text"]}\n{{"score":{_opt_d_score}}}{options["option_d"]["text"]}')
        # _format = (f'{{"score":{_opt_a_score}}}{options["option_a"]["text"]}\n{{"score":{_opt_b_score}}}{quiz["option_b"]}\n{{"score":{_opt_c_score}}}{quiz["option_c"]}\n{{"score":{_opt_d_score}}}{quiz["option_d"]}')

        return _format
    def save_quiz_format(self, _content, filepath):
        """Save the quiz format to a file"""
        with open(filepath, 'w+', encoding='utf-8') as file: # "a+ MEANS append, w+ MEANS create/overwrite"
            file.write(_content)

    def main(self):
        """Main function"""

        ### USER SELECTS TEST BANK TYPE AND SUBJECT AREA
        subject = "General" # USER ACTION REQ: pick a subject area ### "Data Sources", "Data Warehouse", etc.
        _qbank_type_key = "3" # USER ACTION REQ: pick a type (1-3) ### {"1": "MUST", "2": "SHOULD", "3": "COULD"}
        _dt_year_month = "2024_01" # USER ACTION REQ: pick a year and month ### "2024_01" or "2024_02"

        _types = {
            "1": "MUST" 
            , "2": "SHOULD"
            , "3": "COULD"
            , "4": "PRACTICE"
            , "5": "z_testing"
        }
        # set the 
        if _qbank_type_key is "1" or "2" or "3": # PRODUCTION question banks
            _folder = f"({_dt_year_month}) {subject}"
            _category = f"({_dt_year_month}) {subject} KNOW"

        elif _qbank_type_key is "4": # PRACTICE question bank
            _folder = f"({_dt_year_month}) PRACTICE - {subject}"
            _category = f"({_dt_year_month}) PRACTICE QUESTIONS"

        elif _qbank_type_key is "5": # TESTING (internal dev) question bank
            _folder = f"({_dt_year_month}) z__testing {subject} "
            _category = f"({_dt_year_month}) z_testing"

        test_bank_type = _types[_qbank_type_key]
        sub_lower = subject.lower().replace(" ", "_")
        _quiz_path = f"..\\CONTENT_STORE\\_cs_5_final_format\\subjects\\{subject}\\{test_bank_type}.json" # look for human - approved questions, and store all in archive, for training data
        _raw = self.read_json(_quiz_path)
        c_quiz = ""

        for _q_idx, _q_items in _raw.items():
            # _folder = f"(2024_01) PRACTICE - {subject}"
            # _category = "(2024_01) PRACTICE QUESTIONS"
            # _category = f"(2024_01) {test_bank_type} KNOW"
            _header = self.make_quiz_format_head(folder=_folder, category=_category, quiz=_q_items, shuffle=True, direction="column")
            _scores = self.make_quiz_format_scores(quiz=_q_items, num_correct_options=1)
            _new_line = "".join([_header, "\n\n",  str(_scores), '\n-\n'])
            c_quiz += _new_line
        if c_quiz[-3:] == '\n-\n':
            c_quiz = c_quiz[:-3]
        print(c_quiz)

        _practice_test = f"..\\CONTENT_STORE\\_cs_5_final_format\\subjects\\{subject}\\{sub_lower}_{test_bank_type}.txt"
        _normal_test = f"..\\CONTENT_STORE\\_cs_5_final_format\\subjects\\{subject}\\{sub_lower}_{test_bank_type}_KNOW.txt"
        self.save_quiz_format(c_quiz, _practice_test)

if __name__=='__main__':
    upload_formatter = UploadFormatter()
    upload_formatter.main()