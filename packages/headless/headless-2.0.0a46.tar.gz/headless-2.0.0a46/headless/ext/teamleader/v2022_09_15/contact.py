# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import TypeVar

from ..resource import TeamleaderResource


T = TypeVar('T', bound='Contact')


class Contact(TeamleaderResource):
    id: str
    first_name: str | None = None
    last_name: str
    tags: list[str] = []

    @classmethod
    def get_create_url(cls, *params: Any) -> str:
        return f'{cls._meta.base_endpoint}.add'

    @classmethod
    def get_link_url(cls) -> str:
        return f'{cls._meta.base_endpoint}.linkToCompany'
    
    async def link_company(self, company_id: str, decision_maker: bool = False):
        response = await self._client.post(
            url=self.get_link_url(),
            json={
                'id': self.id,
                'company_id': company_id,
                'decision_maker': decision_maker
            }
        )
        response.raise_for_status()


    class Meta(TeamleaderResource.Meta): # type: ignore
        base_endpoint: str = '/contacts'