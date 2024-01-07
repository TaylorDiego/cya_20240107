"""Run the quiz maker scripts in order"""

from url_loader import UrlLoader
from question_maker import QuestionMaker
# import logging


class QuizFrog:
    """Run the quiz maker scripts in order"""

    def __init__(self):
        self.url_loader = UrlLoader()
        self.question_maker = QuestionMaker()

    def main(self):
        # logging.basicConfig(filename="app.log", level=logging.INFO)
        try:
            self.url_loader.main()
            self.question_maker.main()
        except ValueError as ve:
            print("A ValueError occurred: %s", ve)
            # logging.error("A ValueError occurred: %s", ve)
        except TypeError as te:
            print("A TypeError occurred: %s", te)
            # logging.error("A TypeError occurred: %s", te)

if __name__ == '__main__':
    QuizFrog().main()