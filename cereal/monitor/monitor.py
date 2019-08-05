import os
import logging
import telegram

from apscheduler.schedulers.background import BackgroundScheduler
from ..utils.wrapper import Wrapper


class Monitor(object):

    def __init__(self, url, config, bot=False, chain_id='M'):
        self.url = url
        self.config = config
        self.chain_id = chain_id
        self.wrapper = Wrapper(url)

        if bot:
            self._init_bot()
        self._init_scheduler()

        self.logger = logging.getLogger(__name__)

    def _init_bot(self):
        self.bot_chatID = self.config.get("telegram", []).get("bot_chatID", [])
        bot_token = self.config.get("telegram", []).get("bot_token", [])
        self.bot = telegram.Bot(token=bot_token)
        self.bot.send_message(self.bot_chatID, 'Hi, this is cereal, chat bot inited!')
        self.logger.debug("Inited telegram bot")

    def _init_scheduler(self):
        job_defaults = {'coalesce': False, 'max_instances': 5}
        self.scheduler = BackgroundScheduler(timezone="UTC", job_defaults=job_defaults)

    def trigger(self, address):
        url_tx = os.path.join('transactions', 'address', address, 'limit', '1000')
        print(url_tx)
        data = self.wrapper.request(url_tx)
        print(data)

