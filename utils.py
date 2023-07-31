import os
import re

from pathlib import Path


def get_files_from_dir(root_folder: Path) -> list[str]:
    for folder, _, files in os.walk(root_folder):
        return [os.path.join(folder, file_name) for file_name in files]


def normalize_text(phrase):
    return phrase.lstrip().replace('\n', ' ')


def parse_splitting_text(lines: list):
    questions = []
    answers = []
    for line in lines:
        if re.match(r'Вопрос \d+:', line):
            questions.append(normalize_text(line))
        elif 'Ответ:' in line:
            answers.append(normalize_text(line))
    return dict(zip(questions, answers))
