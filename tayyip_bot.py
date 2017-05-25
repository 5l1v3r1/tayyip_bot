import telebot
import time
import sys
import logging
from telebot import types
import requests
import json
from fuzzywuzzy import process

API_TOKEN = ''

bot = telebot.TeleBot(API_TOKEN)
telebot.logger.setLevel(logging.DEBUG)


def init():
    results = []
    repo_url = 'https://api.github.com/repos/yalanyali/tayyip_bot/contents/sounds'
    r = requests.get(repo_url)
    sounds = json.loads(r.text or r.content)
    for sound in sounds:
        name = sound["name"].split('.')[0].replace('_', ' ')
        url = sound["download_url"]
        results.append([name, url])
    return results


sounds, urls = zip(*init())


@bot.inline_handler(lambda query: len(query.query) > 2)
def query_text(inline_query):
    try:
        results = process.extract(inline_query.query, sounds, limit=4)
        result_list = []

        for result in results:
            i = results.index(result)
            r = types.InlineQueryResultAudio(
                str(i + 1), urls[sounds.index(result[0])], result[0])
            result_list.append(r)

        bot.answer_inline_query(inline_query.id, result_list)
    except Exception as e:
        print(e)


def main_loop():
    bot.polling(True)
    while 1:
        time.sleep(3)


if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print >> sys.stderr, '\nExiting by user request.\n'
        sys.exit(0)
