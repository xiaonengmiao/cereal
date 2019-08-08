__copyright__ = "Copyright (C) 2019 Techcat_ Haohan Li"

__license__ = """
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

__doc__ = """
:mod:`cereal.chatbot.chatbot` provides a chat bot for Cereal.
"""

import logging
import requests
import telegram

from time import sleep
from telegram.error import NetworkError, Unauthorized

# KEY = '4831402b6fad4fc78293db9f99972435'
KEY = '02286ed1a6b50fb5de05fcad202093e4'


def get_response(msg):
    api_url = 'http://www.tuling123.com/openapi/api'
    data = {
        'key': KEY,
        'info': msg,
        'userid': 'wechat-robot',
    }
    try:
        r = requests.post(api_url, data=data).json()
        return r.get('text')
    except requests.exceptions.RequestException:
        return


update_id = None


def chatbot(token):
    """Run the bot."""

    logger = logging.getLogger(__name__)
    global update_id
    # Telegram Bot Authorization Token
    bot = telegram.Bot(token)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.get_updates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        try:
            echo(bot)
        except NetworkError:
            sleep(1)
        except Unauthorized:
            # The user has removed or blocked the bot.
            update_id += 1


def echo(bot):
    """Echo the message the user sent."""
    global update_id
    # Request updates after the last update_id
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1

        if update.message and update.message.text[:4] == '微软小冰':  # your bot can receive updates without messages
            # Reply to the message
            
            reply = get_response(update.message.text)
            default_reply = update.message.text
            print(reply + "\n")
            update.message.reply_text(reply or default_reply)
