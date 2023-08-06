# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

from .picqerresource import PicqerResource
from .productfield import ProductField
from .productpricelist import ProductPricelist
from .productstock import ProductStock


class Product(PicqerResource):
    idproduct: int
    idvatgroup: int
    name: str
    price: float
    fixedstockprice: float | None = None
    idsupplier: int | None = None
    productcode: str
    productcode_supplier: str | None = None
    deliverytime: int | None = None
    description: str | None = None
    barcode: str | None = None
    type: str | None = None
    unlimitedstock: bool = False
    weight: int | None = None
    length: int | None = None
    width: int | None = None
    height: int | None = None
    minimum_purchase_quantity: int | None = None
    purchase_in_quantities_of: int | None = None
    hs_code: str | None = None
    country_of_origin: str | None = None
    active: bool = True
    idfulfilment_customer: int | None = None
    analysis_pick_amount_per_day: float | None = None
    pricelists: list[ProductPricelist] = []

    # Not documented but present in response and Picqer examples.
    productfields: list[ProductField] = []
    images: list[str] = []
    stock: list[ProductStock] = []

    def get_persist_url(self) -> str:
        return self.get_retrieve_url(self.idproduct)

    def get_product_field(self, idproductfield: int) -> Any | None:
        for field in self.productfields:
            if field.idproductfield == idproductfield:
                value = field.value
                break
        else:
            value = None
        return value
    
    def get_total_free_stock(self, idwarehouse: int | None = None) -> int:
        stock: int = 0
        for warehouse in self.stock:
            if idwarehouse is not None and warehouse.idwarehouse != idwarehouse:
                continue
            stock += warehouse.freestock
        return stock

    async def link_location(self, idlocation: int) -> None:
        """Links the specified location to this :class:`Product`."""
        response = await self._client.post(
            url=f'{self.get_persist_url()}/locations',
            json={'idlocation': idlocation}
        )
        response.raise_for_status()

    class Meta:
        base_endpoint: str = '/v1/products'