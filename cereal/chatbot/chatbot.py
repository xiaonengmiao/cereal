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

import os
import json
import logging
import requests
import telegram
import pandas as pd

from time import sleep
from . import ChatBotBase
from ..utils.wrapper import Wrapper
from ..utils.tools import make_visualizer
from telegram.error import NetworkError, Unauthorized


class ChatBot(ChatBotBase):
    """Class for ChatBot."""

    def __init__(self, url, bot_token):
        super().__init__(url, bot_token)
        self.update_id = None
        self.wrapper = Wrapper(url)

        self._init_bot()

        self.logger = logging.getLogger(__name__)

    def _init_bot(self):
        # Telegram Bot Authorization Token
        self.bot = telegram.Bot(token=self.bot_token)

    def run(self):
        """Run the bot."""
        # get the first pending update_id, this is so we can skip over it in case
        # we get an "Unauthorized" exception.
        try:
            self.update_id = self.bot.get_updates()[0].update_id
        except IndexError:
            self.update_id = None

        while True:
            try:
                self.echo(self.bot)
            except NetworkError:
                sleep(1)
            except Unauthorized:
                # The user has removed or blocked the bot.
                self.update_id += 1

    def echo(self, bot):
        """Echo the message the user sent."""
        # Request updates after the last update_id
        for update in bot.get_updates(offset=self.update_id, timeout=10):
            self.update_id = update.update_id + 1

            if update.message:
                # and update.message.text[:4] == '微软小冰':  # your bot can receive updates without messages
                # Reply to the message
                message = update.message.text
                if update.message.text[0] == '/':
                    try:
                        reply = self.get_response(message[1:])
                    except KeyError:
                        reply = None
                        self.logger.info('{} is not valid address'.format(message[1:]))
                        update.message.reply_text('{} is not valid address'.format(message[1:]))
                    if isinstance(reply, pd.DataFrame) and not reply.empty:
                        self.logger.info(reply)
                        reply.to_csv('/tmp/cereal_chat_bot.csv')
                        with open('/tmp/cereal_chat_bot.csv', 'rb') as cereal_chat_bot_txs:
                            update.message.reply_document(cereal_chat_bot_txs)
                        os.remove('/tmp/cereal_chat_bot.csv')
                    elif isinstance(reply, str) and reply:
                        self.logger.info(reply)
                        update.message.reply_text(reply)
                else:
                    # reply = get_response_tuling(message)
                    # self.logger.info(reply)
                    # update.message.reply_text(reply)
                    default_reply = message
                    update.message.reply_text(default_reply)

    def get_response(self, msg):
        if len(msg) > 0:
            if msg[0] == 'A':
                url = os.path.join('transactions', 'address', msg, 'limit', '20')
                txs = self.wrapper.request(url)[0]
                return make_visualizer(txs)
            elif msg == 'height':
                url = os.path.join('blocks', 'height')
                response = self.wrapper.request(url)
                return json.dumps(response)
            elif msg == 'lastblock':
                url = os.path.join('blocks', 'last')
                response = self.wrapper.request(url)
                return json.dumps(make_visualizer(response, 'block'))
            elif msg == 'allslotsinfo':
                url = os.path.join('consensus', 'allSlotsInfo')
                response = self.wrapper.request(url)
                return make_visualizer(response, 'allslotsinfo')
            else:
                return
        else:
            return


# KEY = '4831402b6fad4fc78293db9f99972435'
KEY = '02286ed1a6b50fb5de05fcad202093e4'


def get_response_tuling(msg):
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



