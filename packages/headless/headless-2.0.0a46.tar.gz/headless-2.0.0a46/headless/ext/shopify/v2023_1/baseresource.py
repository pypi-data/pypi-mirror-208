# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from ..resource import ShopifyResource


class BaseResource(ShopifyResource):
    __abstract__: bool = True
    id: int

    @classmethod
    def enveloped(cls, dto: dict[str, Any]) -> dict[str, Any]:
        return {str.lower(cls.__name__): dto}