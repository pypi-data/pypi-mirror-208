# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

import cbra.core as cbra
from ..types import IFrontendStorage


__all__: list[str] = ['ClientStorage']


async def get(
    storage: IFrontendStorage = cbra.instance('_AuthorizationClientStorage')
) -> IFrontendStorage:
    return storage


ClientStorage: IFrontendStorage = fastapi.Depends(get)