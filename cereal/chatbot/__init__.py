__copyright__ = "Copyright (C) 2019 Haohan Li"

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
:mod:`cereal.chatbot` provides a chat bot for Cereal.
"""


class ChatBotBase(object):
    """Base Class for chat bot used as service agent.

    It can be used to create a chatbot for refering vsys info,
    using Telegram chatbot as base.

    .. attribute:: bot_token

        Telegram chatbot token.

    .. attribute:: url

        VSYS full node url with which to get info.
    """

    def __init__(self, url=None, bot_token="Talk to https://telegram.me/botfather to get one!"):
        """Constructor."""
        self.url = url
        self.bot_token = bot_token

    def __repr__(self):
        """Returns internal representation used for refering."""
        return repr(self.bot_token)

    def __str__(self):
        """Returns readable representation."""
        return str(self.bot_token)
