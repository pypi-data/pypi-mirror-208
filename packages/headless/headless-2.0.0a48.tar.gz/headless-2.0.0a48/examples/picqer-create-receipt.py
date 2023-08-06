# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import os

from headless.ext.picqer import Client
from headless.ext.picqer import PurchaseOrder


async def main():
    params = {
        'api_key': os.environ['PICQER_API_KEY'],
        'api_email': 'test@headless.python.dev.unimatrixone.io',
        'api_url': os.environ['PICQER_API_URL']
    }
    async with Client(**params) as client:
        po = await client.retrieve(PurchaseOrder, 1523542)
        receipt = await po.create_receipt(remarks="Aangemaakt via Apparaategistratiesysteem")

        try:
            await receipt.receive(19666711)
            await receipt.receive(23286042, 3)
            print(receipt.json(indent=2))
            input("Press enter to delete")
        finally:
            await receipt.delete()


if __name__ == '__main__':
    asyncio.run(main())