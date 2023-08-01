import os
import re

from enum import Enum


class QuizButtons(Enum):
    new = 'Новый вопрос'
    give_up = 'Сдаться'
    my_score = 'Мой счет'


def normalize_answer(answer: str) -> str:
    answer = answer.rstrip('.').strip().replace('"', '')
    normalized_answer = re.sub(r'[\(\[].*?[\)\]]', '', answer).lower()
    return normalized_answer


def parse_quiz(scan_folder: str = 'questions') -> list:
    quiz_questions = []

    for folder, _, files in os.walk(scan_folder):
        for filename in files:
            file_path = os.path.join(folder, filename)
            with open(file_path, 'r', encoding='KOI8-R') as file:
                content = file.read()

            pattern = r'Вопрос \d+:(.*?)Ответ:(.*?)\n\n'
            matches = re.findall(pattern, content, re.DOTALL)

            for match in matches:
                question = match[0].strip().replace('\n', '')
                answer = match[1].strip()
                quiz_questions.append({
                    'question': question,
                    'answer': normalize_answer(answer)
                })
    return quiz_questions
