# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
import xml.etree.ElementTree as etree

import httpx
from headless.core.httpx import Client
from .credential import VIESCredential
from .viesresult import VIESResult


class VIESClient(Client):
    __module__: str = 'headless.ext.vies'

    @classmethod
    def test(cls) -> 'VIESClient':
        return cls(
            base_url="https://viesapi.eu/api-test/",
            api_id='test_id',
            api_key='test_key'
        )
    
    def __init__(
        self,
        api_id: str,
        api_key: str,
        *,
        base_url: str = 'https://viesapi.eu/api',
        **kwargs: Any
    ):
        credential = VIESCredential(api_id, api_key)
        super().__init__(base_url=base_url, credential=credential, **kwargs)

    async def lookup(self, vat: str, max_retries: int = 10, _attempts: int = 0) -> VIESResult:
        """Lookup an EU Value Added Tax (VAT) identification
        number.
        """
        try:
            response = await self.get(url=f'/get/vies/euvat/{vat}')
        except httpx.ReadTimeout:
            _attempts += 1
            if _attempts > max_retries:
                raise
            self.logger.warning("VIES timeout, retrying (attempt: %s)", _attempts)
            return await self.lookup(vat, max_retries=max_retries, _attempts=_attempts)
        response.raise_for_status()
        root = etree.fromstring(bytes.decode(response.content))
        return VIESResult.parse_obj({
            child.tag: child.text
            for child in (root.find('vies') or [])
        })
