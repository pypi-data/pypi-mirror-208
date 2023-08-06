# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .irefreshtoken import IRefreshToken
from .objectidentifier import ObjectIdentifier


class RefreshTokenIdentifier(ObjectIdentifier[IRefreshToken]):
    openapi_title: str = 'Refresh Token ID'
    openapi_format: str = 'string'