import random

import redis
import vk_api as vk

from environs import Env

from vk_api.keyboard import VkKeyboardColor
from vk_api.keyboard import VkKeyboard
from vk_api.longpoll import VkLongPoll
from vk_api.longpoll import VkEventType
from vk_api.utils import get_random_id

from quiz_helpers import parse_quiz
from quiz_helpers import QuizButtons


def handle_new_question_request(event, api, keyboard, quiz, db):
    choice = random.choice(quiz)
    db.set(event.user_id, choice['answer'])
    api.messages.send(
        user_id=event.user_id,
        message=choice['question'],
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def handle_score_request(event, api, keyboard):
    api.messages.send(
        user_id=event.user_id,
        message='Эта функция будет доступна позднее.',
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )


def handle_give_up_request(event, api, keyboard, quiz, db):
    answer = db.get(event.user_id)
    api.messages.send(
        user_id=event.user_id,
        message=answer,
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )
    api.messages.send(
        user_id=event.user_id,
        message='Не расстраивайся! В следующий раз обязательно получится!',
        random_id=get_random_id(),
        keyboard=keyboard.get_keyboard(),
    )
    handle_new_question_request(event, api, keyboard, quiz, db)


def handle_solution_attempt(event, api, keyboard, quiz, db):
    correct_answer = db.get(event.user_id)
    user_answer = event.text.strip('"[]() ').lower()

    if user_answer == correct_answer:
        api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю!',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )
        handle_new_question_request(event, api, keyboard, quiz, db)
    else:
        api.messages.send(
            user_id=event.user_id,
            message='Неправильно… Попробуешь ещё раз?',
            random_id=get_random_id(),
            keyboard=keyboard.get_keyboard(),
        )


if __name__ == '__main__':
    env = Env()
    env.read_env()

    vk_bot_token = env('VK_BOT_TOKEN')
    redis_db_host = env('REDIS_DB_HOST', 'localhost')
    redis_db_port = env.int('REDIS_DB_PORT', 6379)
    quiz_path = env('QUIZ_PATH', 'questions')

    quiz_questions = parse_quiz(quiz_path)
    db_conn = redis.Redis(
        host=redis_db_host,
        port=redis_db_port,
        db=1,
        decode_responses=True,
    )

    vk_session = vk.VkApi(token=vk_bot_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    vk_keyboard = VkKeyboard(one_time=True)
    vk_keyboard.add_button(QuizButtons.new.value,
                           color=VkKeyboardColor.PRIMARY)
    vk_keyboard.add_button(QuizButtons.give_up.value,
                           color=VkKeyboardColor.NEGATIVE)
    vk_keyboard.add_line()
    vk_keyboard.add_button(QuizButtons.my_score.value)

    for vk_event in longpoll.listen():
        if vk_event.type == VkEventType.MESSAGE_NEW and vk_event.to_me:
            args = [vk_event, vk_api, vk_keyboard, quiz_questions, db_conn]
            match vk_event.text:
                case QuizButtons.give_up.value:
                    handle_give_up_request(*args)
                case QuizButtons.new.value:
                    handle_new_question_request(*args)
                case QuizButtons.my_score.value:
                    handle_score_request(vk_event, vk_api, vk_keyboard)
                case _:
                    handle_solution_attempt(*args)
