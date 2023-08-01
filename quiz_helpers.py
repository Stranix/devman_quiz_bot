import os
import re
import logging

from enum import Enum

logger = logging.getLogger(__name__)


class QuizButtons(Enum):
    new = 'Новый вопрос'
    give_up = 'Сдаться'
    my_score = 'Мой счет'


def normalize_answer(answer):
    answer = answer.rstrip('.').strip().replace('"', '')
    normalized_answer = re.sub(r'[\(\[].*?[\)\]]', '', answer).lower()
    return normalized_answer


def parse_quiz(scan_folder='questions'):
    logger.info('Собираем вопросы для викторы из папки %s', scan_folder)
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
    logger.info('Вопросы получены')
    return quiz_questions
