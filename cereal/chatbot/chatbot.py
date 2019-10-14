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
import telegram
import requests, re
import pandas as pd

from time import sleep
from . import ChatBotBase
from urllib.parse import quote
from ..utils.wrapper import Wrapper
from ..utils.tools import make_visualizer
from telegram.error import NetworkError, Unauthorized


class ChatBot(ChatBotBase):
    """Class for ChatBot.

    It can be used to create a chatbot for refering vsys info,
    using Telegram chatbot as base.

    .. attribute:: bot

        Telegram chatbot.

    .. attribute:: url

        VSYS full node url with which to get info.
    """

    def __init__(self, url, bot_token):
        """Constructor."""
        super().__init__(url, bot_token)
        self.update_id = None
        self.wrapper = Wrapper(url)

        self._init_bot()

        self.logger = logging.getLogger(__name__)

    def _init_bot(self):
        """Telegram Bot Authorization Token."""
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
                if not update.message.text and update.message.sticker:
                    update.message.reply_sticker(update.message.sticker)
                else:
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
                        reply = get_response_xiaomi(message)
                        self.logger.info(reply)
                        update.message.reply_text(reply, parse_mode=telegram.ParseMode.MARKDOWN)
                        # default_reply = message
                        # update.message.reply_text(default_reply)

    def get_response(self, msg):
        if len(msg) > 0:
            if msg.startswith('transaction'):
                url = os.path.join('transactions', 'address', msg.split(':')[-1].strip(), 'limit', '20')
                txs = self.wrapper.request(url)[0]
                return make_visualizer(txs)
            elif msg.startswith('height'):
                url = os.path.join('blocks', 'height')
                response = self.wrapper.request(url)
                return json.dumps(response)
            elif msg.startswith('lastblock'):
                url = os.path.join('blocks', 'last')
                response = self.wrapper.request(url)
                return json.dumps(make_visualizer(response, 'block'))
            elif msg.startswith('allslotsinfo'):
                url = os.path.join('consensus', 'allSlotsInfo')
                response = self.wrapper.request(url)
                return make_visualizer(response, 'allslotsinfo')
            elif msg.startswith('balance'):
                url = os.path.join('addresses', 'balance', msg.split(':')[-1].strip())
                response = self.wrapper.request(url)
                return json.dumps(make_visualizer(response, 'balance'))
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

def get_response_xiaomi(msg):
    ini = "{'sessionId':'09e2aca4d0a541f88eecc77c03a8b393','robotId':'webbot','userId':'462d49d3742745bb98f7538c42f9f874','body':{'content':'" + msg + "'},'type':'txt'}&ts=1529917589648"
    url = "http://i.xiaoi.com/robot/webrobot?&callback=__webrobot_processMsg&data=" + quote(ini)
    cookie = {"cnonce": "808116", "sig": "0c3021aa5552fe597bb55448b40ad2a90d2dead5",
              "XISESSIONID": "hlbnd1oiwar01dfje825gavcn", "nonce": "273765", "hibext_instdsigdip2": "1"}
    try:
        r = requests.get(url, cookies=cookie)
        pattern = re.compile(r'\"fontColor\":0,\"content\":\"(.*?)\",\"emoticons')
        r = pattern.findall(r.text)
        rep = {"\\n": "\n", "\\t": "\t", "\\r": "\r", "\\u003c": "<", "\\u003e": ">",
               "\\u003d": "=", "\\": "", "[link url\\u003d": "", "[/link]": "", "]": "", "[": ""} # define desired replacements here
        # use these three lines to do the replacement
        rep = dict((re.escape(k), v) for k, v in rep.items())
        #Python 3 renamed dict.iteritems to dict.items so use rep.items() for latest versions
        pattern = re.compile("|".join(rep.keys()))
        # pattern = re.compile('\\\\n|\\\\t|\\\\r')
        r = pattern.sub(lambda m: rep[re.escape(m.group(0))], r[1])
        return r
    except requests.exceptions.RequestException:
        return
