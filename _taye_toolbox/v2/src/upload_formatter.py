import json

def read_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def make_quiz_format_head(folder, category, quiz, shuffle=True, direction="column"):
    _folder = f'"folder":"{folder}"'
    _tags = ',"tags":{'+ f'"category":"{category}"'+ '}'
    _shuffle = f'"shuffle":{str(shuffle).lower()}'
    _block = f',"points":[1,0], "min":1, "max":1, {_shuffle}, "display":{{"direction":"{direction}"}}'
    _question = quiz["question"]
    c_format = '{' + ''.join([_folder,_tags,_block]) + '}' + f'{_question}'
    return c_format

def make_quiz_format_scores(quiz, num_correct_options):
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
def save_quiz_format(_content, filepath):
    with open(filepath, 'w+') as file: # "a+ MEANS append, w+ MEANS create/overwrite"
        file.write(_content)

def main():
    _quiz_path = "..\\4_HUMAN_CHECK\\human_check.json" # look for human - approved questions, and store all in archive, for training data
    _raw = read_json(_quiz_path)
    c_quiz = ""
    for _q_idx, _q_items in _raw.items():
        _header = make_quiz_format_head(folder="test_folder", category="abc_category", quiz=_q_items, shuffle=True, direction="column")
        _scores = make_quiz_format_scores(quiz=_q_items, num_correct_options=1)
        _new_line = "".join([_header, "\n\n",  str(_scores), '\n-\n'])
        c_quiz += _new_line
    if c_quiz[-3:] == '\n-\n':
        c_quiz = c_quiz[:-3]
    print(c_quiz)
    save_quiz_format(c_quiz, "..\\5_FINAL_FORMAT\\_bulk_question_upload__testinvite.txt")

if __name__=='__main__':
    main()