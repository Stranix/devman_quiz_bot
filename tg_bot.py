import random

import redis

from environs import Env

from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)

from quiz_helpers import QuizButtons
from quiz_helpers import parse_quiz

NEW_QUESTION, ANSWER = range(2)


def start(update, _):
    quiz_keyboard = [
        [QuizButtons.new.value, QuizButtons.give_up.value],
        [QuizButtons.my_score.value, ]
    ]
    reply_markup = ReplyKeyboardMarkup(quiz_keyboard)

    update.message.reply_text(
        "Привет! Я бот для викторины!",
        reply_markup=reply_markup
    )
    return NEW_QUESTION


def handle_new_question_request(update, context):
    choice = random.choice(context.bot_data['quiz'])
    update.message.reply_text(choice['question'])

    db = context.bot_data["db"]
    db.set(update.message.chat_id,  choice['answer'])
    return ANSWER


def handle_solution_attempt(update, context):
    db = context.bot_data["db"]
    correct_answer = db.get(update.message.chat_id)
    user_answer = update.message.text.strip('"[]() ').lower()
    print('correct_answer', correct_answer)
    print('пользователь написал:', user_answer)

    if user_answer == correct_answer:
        update.message.reply_text('Правильно! Поздравляю!')
        handle_new_question_request(update, context)
    else:
        print('пользователь написал:', user_answer)
        update.message.reply_text('Неправильно… Попробуешь ещё раз?')
        return ANSWER


def handle_give_up_request(update, context):
    db = context.bot_data["db"]
    answer = db.get(update.message.chat_id)
    update.message.reply_text(answer)
    update.message.reply_text(
        'Не расстраивайся! В следующий раз обязательно получится!'
    )
    handle_new_question_request(update, context)


def cancel(update, _):
    update.message.reply_text(
        'До новых встреч!',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


if __name__ == '__main__':
    env = Env()
    env.read_env()

    tg_bot_api_key = env('TG_BOT_TOKEN')
    redis_db_host = env('REDIS_DB_HOST', 'localhost')
    redis_db_port = env.int('REDIS_DB_PORT', 6379)

    quiz_questions = parse_quiz()
    db_conn = redis.Redis(
        host=redis_db_host,
        port=redis_db_port,
        db=0,
        decode_responses=True,
    )

    updater = Updater(tg_bot_api_key)

    dispatcher = updater.dispatcher
    dispatcher.bot_data["db"] = db_conn
    dispatcher.bot_data["quiz"] = quiz_questions

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEW_QUESTION: [
                MessageHandler(Filters.regex(r'^Новый вопрос'),
                               handle_new_question_request),
            ],
            ANSWER: [
                MessageHandler(Filters.regex(r'^Сдаться'),
                               handle_give_up_request),
                MessageHandler(Filters.text, handle_solution_attempt),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()
