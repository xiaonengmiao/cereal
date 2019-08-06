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
:mod:`cereal.monitor.monitor` provides monitoring ability for Cereal. 
"""

import os
import time
import logging
import telegram

from ..utils.wrapper import Wrapper
from ..utils.tools import make_visualizer


class Monitor(object):
    """Class for monitoring."""

    def __init__(self, url, config, bot=False, chain_id='M'):
        self.url = url
        self.config = config
        self.chain_id = chain_id
        self.wrapper = Wrapper(url)

        if bot:
            self._init_bot()
        else:
            self.bot = None

        self.logger = logging.getLogger(__name__)

    def _init_bot(self):
        self.bot_chatID = self.config.get("telegram", []).get("bot_chatID", [])
        bot_token = self.config.get("telegram", []).get("bot_token", [])
        self.bot = telegram.Bot(token=bot_token)
        self.bot.send_message(self.bot_chatID, 'Hi, this is cereal, chat bot inited!')

    def trigger(self, address=None):
        if address:
            url_tx = os.path.join('transactions', 'address', address, 'limit', '4500')
            txs = self.wrapper.request(url_tx)[0]
            cnt_time = int(time.time()*1000000000)//6000000000*6000000000
            check_time = 5*60*1000000000
            txs = [x for x in txs if x['timestamp'] > cnt_time-check_time]
            # txs = txs[:10]
            if txs:
                df = make_visualizer(txs)
                self.logger.info(df)
                if self.bot:
                    for index, row in df.iterrows():
                        self.bot.send_message(self.bot_chatID, row.to_string())
            return txs
        else:
            for s in self.config.get("address", []):
                self.trigger(s)

