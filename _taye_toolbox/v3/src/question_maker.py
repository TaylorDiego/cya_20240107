"""This script loads a context file and creates an AI output (quiz)."""

from openai import OpenAI
import yaml



CONFIG = yaml.safe_load(open('..\\config\\config.yaml', 'r', encoding='utf-8'))
CONTEXT = CONFIG["CONTEXT"]
TASK = CONFIG["TASK"]

KEYS = yaml.safe_load(open(CONFIG["KEYS"], 'r', encoding='utf-8'))
OPENAI_API_KEY = KEYS["OPENAI_API_KEY"]

question_types = (
    {
    "(TF) True/False": "Simple True or False questions, with a single correct answer."
    , "(MC) Multiple choice": "Multiple Choice (a, b, c, d) questions, with a single correct answer."
    , "(FB) Fill-in-the-blank": "The question is formatted as a complete, and TRUE sentence with a single word ommitted. There should be four (a, b, c, d) possible answers, and only one correct answer. Each option MUST BE A SINGLE WORD."
    }
)

def read_file(file_path):
    """Read a file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def make_questions(text):
    """Make the questions"""
    client = OpenAI(api_key=OPENAI_API_KEY)
    print("\nLet's make a quiz! Here are the question types you can choose from: \n")
    for key, val in question_types.items():
        print(f"{key}")
        # print(f"{key}\n  --> {val}")
    q_format = input("\nChoose a question FORMAT: \n")
    q_count = input("\nChoose a question COUNT: \n")
    q_type = input("\nChoose question PURPOSE: more PRACTICAL or more CONCEPTUAL: \n")
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
               , "content": "You are an expert educator and quiz maker."
            }
            , {"role": "system"
               , "content": f"The user will ask you to make a particular kind of question, or set of questions, from a given text. Make sure to include the question, the answer, and a complete explanation.The user may use short-hand in their request, using this 'legend': {question_types}"
            }
            , {"role": "system", "content": "The user may request a level of abstraction (a 'continuum' ranging from Practical & Applicable to Conceptual & Use Case focused). With this difficulty level indicated, we then need to change the level of exmplanation. For practical questions, there should be a short, complete sentence in the explanation. When the questions are conceptual, the explanation needs to be very clear for all learners to pass the scrutiny of all, in 2-3 sentences, at most, please. "
            }
            , {"role": "user"
            , "content": f"Please make {q_count} {q_format} questions, with a particular focus on {focus} and relative abstraction {q_type} from Conceptual to Practical, using the following contextual information: {text}"
            }
            , {"role": "system"
               , "content": f"Please ensure that the output of each question is in correct, proper JSON format, specifically like this: {_format_json}. That means that you should not 'say anything' only to provide the JSON response."
            }
        ]
    )
    result = response.choices[0].message.content
    # print(result)
    return result

def save_file(file_path, content):
    """Write to a file"""
    with open(file_path, 'w+', encoding='utf-8') as file:
        file.write(content)

def main():
    """Main function"""
    _input = CONTEXT
    _output = TASK
    file_content = read_file(_input)
    response = make_questions(file_content)
    save_file(_output, response)

if __name__ == "__main__":
    main()
 