# Copyright (C) 2022 Cochise Ruhulessin # type: ignore
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Callable
from typing import Iterable
from typing import Iterator
from typing import Mapping
from typing import TypeVar

from headless.ext.shopify.v2023_1.basemetafield import BaseMetafield

from .metafield import Metafield


T = TypeVar('T')


class MetafieldSet(Mapping[str, Metafield]):
    _fields: dict[str, Metafield]

    def __init__(self, metafields: Iterable[Metafield]):
        self._fields = {f'{x.namespace}.{x.key}': x for x in metafields}

    def parse(self, key: str, parser: Callable[..., T] = lambda x: x) -> T:
        return self._fields[key].parse(parser)

    def __getitem__(self, __key: str) -> Metafield:
        return self._fields[__key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._fields)

    def __len__(self) -> int:
        return len(self._fields)