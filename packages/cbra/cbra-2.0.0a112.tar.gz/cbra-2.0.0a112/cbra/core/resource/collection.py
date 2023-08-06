# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import fastapi
from starlette.datastructures import URL

from cbra.types import IQueryResult
from .const import CURSOR_PARAM_NAME
from .resourcemodel import ResourceModel


class Collection:
    __module__: str = 'cbra.core'
    _limit: int
    cursor_param_name: str
    default_limit: int = 100
    max_limit: int
    model: type[ResourceModel]

    async def list(
        self,
        page_token: str | None = fastapi.Query(
            default=None,
            alias=CURSOR_PARAM_NAME,
            title="Pagination token",
            description="Pagination token used to iterate over the collection."
        ),
        limit: int | None = fastapi.Query(
            default=None,
            title="Limit",
            description=(
                "Limits the number of resources included in the result set. "
                "Note that the resource server may impose an arbitrary "
                "limit on the size of the result set, regardless of the "
                "client-provided value of `limit`."
            )
        )
    ) -> Any:
        self._limit = min(self.max_limit, limit or self.default_limit)
        result = await self.filter(
            None,
            page_token=page_token,
            limit=self._limit
        )
        resource =  self.model.__list_model__.parse_obj({
            'apiVersion': 'v1',
            'kind': f'{self.model.__name__}List',
            'metadata': {
                'nextUrl': self.get_next_url(result.token)
            },
            'items': []
        })
        resource.items = [self.adapt(x) for x in result.items] # type: ignore
        return resource

    async def filter(
        self,
        params: Any,
        page_token: str | None,
        limit: int
    ) -> IQueryResult[Any]:
        raise NotImplementedError
    
    def get_next_url(self, token: str | None) -> str | None:
        if not token:
            return None
        url: URL = self.reverse('list', params={self.cursor_param_name: token}) # type: ignore
        url = url.include_query_params( # type: ignore
            limit=self._limit
        )
        return str(url) # type: ignore