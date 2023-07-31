import argparse
import os

from pathlib import Path
from pprint import pprint

from utils import get_files_from_dir, parse_splitting_text


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Загрузчик вопросов викторины'
    )
    parser.add_argument(
        '--qa_path',
        '-p',
        type=Path,
        default='questions',
        help='путь к каталогу с txt-файлами вопросов и ответов',
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    questions = []
    answers = []

    files = get_files_from_dir(args.qa_path)
    for file_name in files:
        with open(file_name, encoding='KOI8-R') as file:
            texts = file.read().split('\n\n')
        print(parse_splitting_text(texts))
