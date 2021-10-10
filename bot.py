import os
import re
import sys

import telebot

import data
import game
from text import text
import util

SECRET_FILE = 'token-secret.txt'

print('got game data', data.game_data)

if not os.path.exists(SECRET_FILE):
    print(f'expecting your Telegram token in {SECRET_FILE}, but file doesn\'t exist')
    sys.exit(1)

secret = util.read_file(SECRET_FILE)
bot = telebot.TeleBot(secret, parse_mode='Markdown') 
game = game.Game()

def bot_send_callback(orig_message, reply_kind, msg_kind, new_message):
    if msg_kind == 'text':
        print('sending group message')
        if reply_kind == 'group':
            bot.send_message(orig_message.chat.id, new_message)
        else:
            bot.reply_to(orig_message, new_message)

    elif msg_kind == 'image':
        print('sending photo')
        bot.send_photo(orig_message.chat.id, new_message)

def make_leaderboard():
    stats = data.leader.summary()
    print('got stats', stats)
    text = []
    for item in stats:
        score = item['score'] or 0
        wins = item['wins'] or 0
        guesses = item['guesses'] or 0
        name = item['name'] or '??'
        text.append(f"{name:>24} - {score:.3f} ({wins}W {guesses}G)")
    text = "\n".join(text)
    return "Current Leaderboard:\n```"+text+"```"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    terms = data.num_terms()
    insults = data.num_insults()
    terms = f'I have **{terms} terms** and **{insults} insults** in my databoose.\n\n'
    greeting = text['greeting'] + terms + make_leaderboard()
    bot.reply_to(message, greeting)

@bot.message_handler(commands=['leader', 'leaders', 'leaderboard', 'stats', 'top'])
def send_leaderboard(message):
    bot.reply_to(message, make_leaderboard())

@bot.message_handler(commands=['new'])
def send_welcome(message):
    if game.new(message, bot_send_callback):
        bot.reply_to(message, text['new__started'])
    else:
        bot.reply_to(message, text['new__inprogress'])

@bot.message_handler(regexp=".*")
def send_guess(message):
    print('got message', message)
    if game.playing():
        words = re.split(r"\s+", message.text)
        if len(words) == 1:
            print('potential guess', words)
            username = message.from_user.username or message.from_user.first_name+" "+message.from_user.last_name
            game.guess(words[0], message, message.from_user.username)
        else:
            print('not for me', message)

bot.infinity_polling(interval=0, timeout=20)

