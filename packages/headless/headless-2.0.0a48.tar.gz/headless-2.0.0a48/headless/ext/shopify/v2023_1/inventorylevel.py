# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import datetime
from datetime import timezone

import pydantic

from ..resource import ShopifyResource


class InventoryLevel(ShopifyResource):
    available: int
    inventory_item_id: int
    location_id: int
    disconnect_if_necessary: bool = False
    updated_at: datetime = pydantic.Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def get_persist_url(self) -> str:
        return f'{self._meta.base_endpoint}/set.json'

    class Meta:
        base_endpoint: str = '/2023-01/inventory_levels'
        name: str = 'inventory_level'
        persist_method: str = 'POST'
        pluralname: str = 'inventory_levels'