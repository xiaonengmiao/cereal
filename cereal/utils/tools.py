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
:mod:`cereal.utils.wrapper` provides useful functions for Cereal.
"""

import pandas as pd

from datetime import datetime


def make_visualizer(txs):
    """Visualise txs in table."""

    df = pd.DataFrame()
    df['timestamp'] = [datetime.fromtimestamp(x['timestamp'] // 1000000000).strftime('%Y-%m-%d %H:%M:%S') for x in txs]
    df['id'] = [x['id'] for x in txs]
    df['height'] = [x['height'] for x in txs]
    df['type'] = [x['type'] for x in txs]
    df['sender'] = [x['proofs'][0]['publicKey'] for x in txs]
    df['receipt'] = [x['receipt'] if 'receipt' in x else None for x in txs]
    df['fee'] = [x['fee']/100000000 for x in txs]
    df['amount'] = ['{:.4f}'.format(x['amount']/100000000) if 'amount' in x else 0 for x in txs]
    df['status'] = [x['status'] for x in txs]
    df['leaseId'] = [x['leaseId'] if 'leaseId' in x else None for x in txs]
    return df
