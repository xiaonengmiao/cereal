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

from . import MonitorBase
from ..utils.wrapper import Wrapper
from ..utils.tools import make_visualizer


class Monitor(MonitorBase):
    """Class for monitoring."""

    def __init__(self, url, bot_chat_id, bot_token, address, bot=False, chain_id='M'):
        super().__init__(url, bot_chat_id, bot_token)
        self.address = address
        self.chain_id = chain_id
        self.wrapper = Wrapper(self.url)

        if bot:
            self._init_bot()
        else:
            self.bot = None

        self.logger = logging.getLogger(__name__)

    def _init_bot(self):
        # Telegram Bot Authorization Token
        self.bot = telegram.Bot(token=self.bot_token)
        self.bot.send_message(self.bot_chat_id, 'Hi, this is cereal, chat bot inited!')

    def trigger(self, address=None):
        if address:
            txs = self._get_txs(address)
            if txs:
                df = make_visualizer(txs)
                self.logger.info(df)
                if self.bot:
                    df.to_csv('/tmp/cereal_monitor_txs.csv')
                    with open('/tmp/cereal_monitor_txs.csv', 'rb') as cereal_monitor_txs:
                        self.bot.send_document(self.bot_chat_id, cereal_monitor_txs)
                    os.remove('/tmp/cereal_monitor_txs.csv')
        else:
            for s in self.address:
                txs = self._get_txs(s)
                if txs:
                    df = make_visualizer(txs)
                    self.logger.info(df)
                    if self.bot:
                        if not os.path.exists('/tmp/cereal_monitor_txs.csv'):
                            df.to_csv('/tmp/cereal_monitor_txs.csv')
                        else:
                            df.to_csv('/tmp/cereal_monitor_txs.csv', mode='a', header=False)
            if os.path.exists('/tmp/cereal_monitor_txs.csv') and self.bot:
                with open('/tmp/cereal_monitor_txs.csv', 'rb') as cereal_monitor_txs:
                    self.bot.send_document(self.bot_chat_id, cereal_monitor_txs)
                os.remove('/tmp/cereal_monitor_txs.csv')

    def _get_txs(self, address):
        url_tx = os.path.join('transactions', 'address', address, 'limit', '4500')
        txs = self.wrapper.request(url_tx)[0]
        cnt_time = int(time.time() * 1000000000) // 6000000000 * 6000000000
        check_time = 5 * 60 * 1000000000
        txs = [x for x in txs if x['timestamp'] > cnt_time-check_time]
        # txs = txs[:2]
        return txs
