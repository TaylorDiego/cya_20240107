from openai import OpenAI
import yaml

OPENAI_API_KEY = yaml.safe_load(open('..\\data\\inputs\\keys.yaml'))['OPENAI_API_KEY']

question_types = (
    {
    "(TF) True/False": "Simple True or False questions, with a single correct answer."
    , "(MC) Multiple choice": "Multiple Choice (a, b, c, d) questions, with a single correct answer."
    , "(FB) Fill-in-the-blank": "The question is formatted as a complete, and TRUE sentence with a single word ommitted. There should be four (a, b, c, d) possible answers, and only one correct answer. Each option MUST BE A SINGLE WORD."
    }
)

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def make_questions(text):
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("\nLet's make a quiz! Here are the question types you can choose from: \n")
    for key, val in question_types.items():
        print(f"{key}")
        # print(f"{key}\n  --> {val}")
    type_questions = input(f"\nChoose a QUESTION TYPE: \n")
    n_questions = input("\nChoose a QUESTION COUNT: \n")
    difficulty = input("\nChoose a QUESTION DIFFICULTY: \n")
    focus = input("\nChoose a few words to FOCUS on as the topic for the question(s): \n")
    _format_json = ({
        "question_1 ": {
            "question": {"_question"}
            , "options": {
                "option_a" : {"_option_a"}
                , "option_b" : {"_option_b"}
                , "option_c" : {"_option_c"}
                , "option_d" : {"_option_d"}
                }
            ,"answer": {"_answer"}
            ,"explanation": {"_explanation"}
        }
        , "question_2": {
            "question": {"_question"}
            , "options": {
                "option_a" : {"_option_a"}
                , "option_b" : {"_option_b"}
                , "option_c" : {"_option_c"}
                , "option_d" : {"_option_d"}
                }
            ,"answer": {"_answer"}
            ,"explanation": {"_explanation"}
        }
        , "question_3": {
            "question": {"_question"}
            , "options": {
                "option_a" : {"_option_a"}
                , "option_b" : {"_option_b"}
                , "option_c" : {"_option_c"}
                , "option_d" : {"_option_d"}
                }
            ,"answer": {"_answer"}
            ,"explanation": {"_explanation"}
        }
    })
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        temperature=0,
        messages=[
            {"role": "system"
             , "content": "You are an expert educator and quiz maker."}
            , {"role": "system"
               , "content": f"The user will ask you to make a particular kind of question, or set of questions, from a given text. Make sure to include the question, the answer, and a concise explanation. The user may use short-hand, using this 'legend': {question_types}"}
            , {"role": "user"
               , "content": f"Please make {n_questions} {type_questions} questions, with a particular focus on {focus} and relative difficulty {difficulty}, using the following contextual information: {text}"}
            , {"role": "system"
               , "content": f"Please ensure that the output of each question is in correct, proper JSON format, specifically like this: {_format_json}. That means that you should not 'say anything' only to provide the JSON response."}
        ]
    )
    result = response.choices[0].message.content
    # print(result)
    return result

def write_file(file_path, content):
    with open(file_path, 'w+') as file:
        file.write(content)

def main():
    input_path = "../data/inputs/context.json"
    output_path = "../data/outputs/quiz.json"
    file_content = read_file(input_path)
    response = make_questions(file_content)
    write_file(output_path, response)

if __name__ == "__main__":
    main()
 