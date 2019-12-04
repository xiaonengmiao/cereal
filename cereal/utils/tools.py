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
:mod:`cereal.utils.wrapper` provides useful functions for Cereal.
"""

import pandas as pd

from datetime import datetime


def make_visualizer(data, vis_type=None):
    """Visualise data in table."""

    if vis_type is None:
        df = pd.DataFrame()
        df['timestamp'] = [datetime.fromtimestamp(x['timestamp'] // 1000000000).strftime('%Y-%m-%d %H:%M:%S') for x in data]
        df['id'] = [x['id'] for x in data]
        df['height'] = [x['height'] for x in data]
        df['type'] = [x['type'] for x in data]
        df['sender'] = [x['proofs'][0]['address'] for x in data]
        df['recipient'] = [x['recipient'] if 'recipient' in x else None for x in data]
        df['fee'] = [x['fee']/100000000 for x in data]
        df['amount'] = ['{:.4f}'.format(x['amount']/100000000) if 'amount' in x else 0 for x in data]
        df['status'] = [x['status'] for x in data]
        df['leaseId'] = [x['leaseId'] if 'leaseId' in x else None for x in data]
        vis = df
    elif vis_type is 'block':
        dic = {'height': data['height'], 'transaction number': data['transaction count'],
               'mint time': datetime.fromtimestamp(data['SPOSConsensus']['mintTime'] // 1000000000).strftime('%Y-%m-%d %H:%M:%S'),
               'mint balance': data['SPOSConsensus']['mintBalance']/100000000,
               'timestamp': datetime.fromtimestamp(data['timestamp'] // 1000000000).strftime('%Y-%m-%d %H:%M:%S'),
               'block size': data['blocksize'], 'fee': data['fee']/100000000,
               'generator': data['generator'], 'signature': data['signature'],
               'recipient': data['transactions'][-1]['recipient']}
        vis = dic
    elif vis_type is 'allslotsinfo':
        df = pd.DataFrame()
        df['slotId'] = [x['slotId'] for x in data[1:] if x['address'] != 'None']
        df['address'] = [x['address'] for x in data[1:] if x['address'] != 'None']
        df['mintingAverageBalance'] = [x['mintingAverageBalance']/100000000 for x in data[1:] if x['address'] != 'None']
        vis = df
    elif vis_type is 'balance':
        if 'balance' in data:
            data['balance'] = data['balance']/100000000
        vis = data
    else:
        raise ValueError("Invalid vis_type %s" % str(vis_type))
    return vis

