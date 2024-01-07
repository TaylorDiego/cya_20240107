import json
import yaml
import os
import sys

def make_quiz_format_head(folder, category, quiz, shuffle=True, direction="column"):
    _folder = f'"folder":"{folder}"'
    _tags = ',"tags":{'+ f'"category":"{category}"'+ '}'
    _shuffle = f'"shuffle":{str(shuffle).lower()}'
    _block = f',"points":[1,0], "min":1, "max":1, {_shuffle}, "display":{{"direction":"{direction}"}}'
    _question = quiz["question"]
    c_format = '{' + ''.join([_folder,_tags,_block]) + '}' + f'{_question}'
    return c_format

def make_quiz_format_scores(quiz, num_correct_options):
    options = {"_option_a":{"percent":0, "text":quiz["option_a"]}, "_option_b":{"percent":0, "text":quiz["option_b"]}, "_option_c":{"percent":0, "text":quiz["option_c"]}, "_option_d":{"percent":0, "text":quiz["option_d"]}}

    # Find the correct option key
    _answer = None
    for key, value in options.items():
        if value["text"] == quiz["answer"]:
            _answer = key
            break

    if _answer is not None:
        options[_answer]["percent"] = float(100/num_correct_options)

    _opt_a_score = options["_option_a"]["percent"]
    _opt_b_score = options["_option_b"]["percent"]
    _opt_c_score = options["_option_c"]["percent"]
    _opt_d_score = options["_option_d"]["percent"]

    _format = (f'{{"score":{_opt_a_score}}}{quiz["option_a"]}\n{{"score":{_opt_b_score}}}{quiz["option_b"]}\n{{"score":{_opt_c_score}}}{quiz["option_c"]}\n{{"score":{_opt_d_score}}}{quiz["option_d"]}')

    return _format

def save_quiz_format(_content, filepath):
    with open(filepath, 'w+') as file:
        file.write(_content)

if __name__=='__main__':
    _quiz = {"question": "What is the capital of the United States?", "answer": "Washington, D.C.", "option_a": "Washington, D.C.", "option_b": "New York City", "option_c": "Los Angeles", "option_d": "Chicago"}
    _header = make_quiz_format_head(folder="test_folder", category="abc_category", quiz=_quiz, shuffle=True, direction="column")
    _scores = make_quiz_format_scores(quiz=_quiz, num_correct_options=1)
    c_quiz = _header + '\n\n' + _scores
    # print(_header)
    # print(_scores)
    print(c_quiz)
    save_quiz_format(c_quiz, "..\\data\\outputs\\test_quiz.txt")