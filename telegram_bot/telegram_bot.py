from telegram import InlineKeyboardButton, KeyboardButton
from typing import Union, List
import telegram_bot
from _model import *
import telegram
from telegram.ext import (   Updater,    CommandHandler,    MessageHandler,    Filters,    CallbackQueryHandler,    PollHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Poll
import time
import datetime
import pyfiglet
import logging
import logging.config
import os
import json
from dotenv import load_dotenv, find_dotenv
from time import sleep

load_dotenv(find_dotenv())

with open('questions.json', 'r') as json_file:
    json_load = json.load(json_file)

data = json_load['questions']


def get_chat_id(update, context):
    chat_id = -1
    
    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]
        print("CHAT ID ---->",chat_id)
    return chat_id


def get_user(update):
    user: User = None
    _from = None
    if update.message is not None:
        _from = update.message.from_user
    elif update.callback_query is not None:
        _from = update.callback_query.from_user

    if _from is not None:
        user = User()
        user.id = _from.id
        user.first_name = _from.first_name if _from.first_name is not None else ""
        user.last_name = _from.last_name if _from.last_name is not None else ""
        user.lang = _from.language_code if _from.language_code is not None else "n/a"

    logging.info(f"from {user}")

    return user

# 🎲 Get ready for the quiz 'testquiz'

# this is testing quiz perpose

# 🖊 2 questions
# ⏱ 10 seconds per question
# 📰 Votes are visible to the quiz owner

# 🏁 Press the button below when you are ready.
# Send /stop to stop it.
def start_command_handler(update, context):
    """Send a message when the command /start is issued."""
    firstname = update.message.from_user.first_name
    lastname = update.message.from_user.last_name
    update.message.reply_text(f'Welcome Dear {firstname}  { lastname} just hit /start command!')
    startButton = [KeyboardButton("Start the quiz now!!!")]
    custom_keyboard = [['top-left', 'top-right'],               ['bottom-left', 'bottom-right']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    update.message.reply_text(text="Game start soon!!",reply_markup=reply_markup)

    update.message.reply_text("""
    🎲 Get ready for the quiz 'testquiz'

this is testing quiz perpose

🖊 2 questions
⏱ 10 seconds per question
📰 Votes are visible to the quiz owner

🏁 Press the button below when you are ready.
Send /stop to stop it.
    """)

    update.message.reply_text("""
    🏁 The quiz 'testquiz' has finished!

You answered 1 question:

✅ Correct – 0
❌ Wrong – 1
⌛️ Missed – 1
⏱ 2.9 sec

🥇1st place out of 1. 

You can take this quiz again but it will not change your place on the leaderboard.""")

    # while True:
    #     play = input("Would you like to start? (Type Y for yes and N for no) ")
    #     if play.upper() == "Y":
    #         sleep (1.0)
    #         update.message.reply_text("Starting in...")
    #         sleep (1.0)
    #         update.message.reply_text("3")
    #         sleep(1.0)
    #         update.message.reply_text("2")
    #         sleep(1.0)
    #         update.message.reply_text("1")
    #         break
    # ##3, 2, 1 countdown added wk.4 friday
    #     elif play.upper() == "N":
    #         update.message.reply_text (f"Goodbye!")
    #         return True
    #     print ("That is not an answer.\n")

    add_typing(update, context)

    quiz_question = QuizQuestion()
    for x in data:
        quiz_question.question = x['question']
        quiz_question.answers = x['answers']
        quiz_question.correct_answer_position = x['correctIndex']
        quiz_question.correct_answer = "28"
        add_quiz_question(update, context, quiz_question)


def help_command_handler(update, context):
    """Send a message when the command /help is issued. """
    update.message.reply_text("Type 😄 /start")

def new_member(update, context):
    logging.info(f"new_member : {update}")

    add_typing(update, context)
    add_text_message(update, context, f"New user")


def main_handler(update, context):
    logging.info(f"update : {update}")

    if update.message is not None:
        user_input = get_text_from_message(update)
        logging.info(f"user_input : {user_input}")

        # reply
        add_typing(update, context)
        add_text_message(update, context, f"You said: {user_input}")

        # ban member
        # m = context.bot.kick_chat_member(
        #     chat_id="-1001572091573", #get_chat_id(update, context),
        #     user_id='1041389347',
        #     timeout=int(time.time() + 86400))
        #
        # logging.info(f"kick_chat_member : {m}")


def poll_handler(update, context):
    # logging.info(f"question : {update.poll.question}")
    # logging.info(f"correct option : {update.poll.correct_option_id}")
    # logging.info(f"option #1 : {update.poll.options[0]}")
    # logging.info(f"option #2 : {update.poll.options[1]}")
    # logging.info(f"option #3 : {update.poll.options[2]}")

    user_answer = get_answer(update)
    logging.info(f"correct option {is_answer_correct(update)}")

    add_typing(update, context)
    add_text_message(update, context, f"Correct answer is {user_answer}")


def add_typing(update, context):
    context.bot.send_chat_action(
        chat_id=get_chat_id(update, context),
        action=telegram.ChatAction.TYPING,
        timeout=1,
    )
    time.sleep(1)


def add_text_message(update, context, message):
    context.bot.send_message(
        chat_id=get_chat_id(update, context), text=message)


def add_suggested_actions(update, context, response):
    options = []

    for item in response.items:
        options.append(InlineKeyboardButton(item, callback_data=item))

    reply_markup = InlineKeyboardMarkup([options])

    context.bot.send_message(
        chat_id=get_chat_id(update, context),
        text=response.message,
        reply_markup=reply_markup,
    )


def add_quiz_question(update, context, quiz_question):
    message = context.bot.send_poll(
        chat_id=get_chat_id(update, context),
        question=quiz_question.question,
        options=quiz_question.answers,
        type=Poll.QUIZ,
        correct_option_id=quiz_question.correct_answer_position,
        open_period=25,
        is_anonymous=True,
        explanation="Well, honestly that depends on what you eat",
        explanation_parse_mode=telegram.ParseMode.MARKDOWN_V2,
    )

    # Save some info about the poll the bot_data for later use in receive_quiz_answer
    context.bot_data.update({message.poll.id: message.chat.id})


def add_poll_question(update, context, quiz_question):
    message = context.bot.send_poll(
        chat_id=get_chat_id(update, context),
        question=quiz_question.question,
        options=quiz_question.answers,
        type=Poll.REGULAR,
        allows_multiple_answers=True,
        is_anonymous=False,
    )


def get_text_from_message(update):
    return update.message.text


def get_answer(update):
    answers = update.poll.options
    ret = ""
    print("answers--->",answers)
    for answer in answers:
        if answer.voter_count == 1:
            ret = answer.text
    return ret


# determine if user answer is correct
def is_answer_correct(update):
    answers = update.poll.options
    ret = False
    counter = 0

    for answer in answers:
        print("answer.voter_count---->",answer.voter_count)
        print("update.poll.correct_option_id---->",update.poll.correct_option_id)
        
        if answer.voter_count == 1 and update.poll.correct_option_id == counter:
            ret = True
            break
        counter = counter + 1
        print("counter---->",counter)
    return ret


def get_text_from_callback(update):
    return update.callback_query.data


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" ', update)
    logging.exception(context.error)


def main():
    updater = Updater(DefaultConfig.TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher

    # command handlers
    dp.add_handler(CommandHandler("help", help_command_handler))
    dp.add_handler(CommandHandler("start", start_command_handler))
    dp.add_handler(CommandHandler("sjd", start_command_handler))

    # message handler
    dp.add_handler(MessageHandler(Filters.text, main_handler))

    dp.add_handler(MessageHandler(      Filters.status_update.new_chat_members, new_member))

    # suggested_actions_handler
    dp.add_handler(
        CallbackQueryHandler(
            main_handler, pass_chat_data=True, pass_user_data=True)
    )

    # quiz answer handler
    dp.add_handler(PollHandler(
        poll_handler, pass_chat_data=True, pass_user_data=True))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    if DefaultConfig.MODE == "webhook":

        updater.start_webhook(
            listen="0.0.0.0",
            port=int(DefaultConfig.PORT),
            url_path=DefaultConfig.TELEGRAM_TOKEN,
        )
        updater.bot.setWebhook(DefaultConfig.WEBHOOK_URL +
                               DefaultConfig.TELEGRAM_TOKEN)

        logging.info(f"Start webhook mode on port {DefaultConfig.PORT}")
    else:
        updater.start_polling()
        logging.info(f"Started.......")

    updater.idle()


class DefaultConfig:
    PORT = int(os.environ.get("PORT", 3978))
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    MODE = os.environ.get("MODE", "polling")
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

    @staticmethod
    def init_logging():
        logging.basicConfig(
            format="%(asctime)s - %(levelname)s - %(message)s",
            level=DefaultConfig.LOG_LEVEL,
        )


if __name__ == "__main__":
    ascii_banner = pyfiglet.figlet_format("SHEKHAR J DHRUV")
    print(ascii_banner)

    # Enable logging
    DefaultConfig.init_logging()

    main()
