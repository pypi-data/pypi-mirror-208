# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import logging
import os

from headless.ext.picqer import Client
from headless.ext.picqer import Receipt


async def main():
    logger: logging.Logger = logging.getLogger('')
    logger.setLevel(logging.DEBUG)
    params = {
        'api_key': os.environ['PICQER_API_KEY'],
        'api_email': 'test@headless.python.dev.unimatrixone.io',
        'api_url': os.environ['PICQER_API_URL']
    }
    async with Client(**params) as client:
        async for receipt in client.listall(Receipt):
            print(f'Receipt {receipt.receiptid}: {receipt.supplier}/{receipt.purchaseorder}')


if __name__ == '__main__':
    asyncio.run(main())