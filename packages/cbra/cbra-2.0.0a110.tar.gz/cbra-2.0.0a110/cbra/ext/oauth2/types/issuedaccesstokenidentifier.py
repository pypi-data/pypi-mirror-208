# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import hashlib

from .objectidentifier import ObjectIdentifier
from .issuedaccesstoken import IssuedAccessToken


class IssuedAccessTokenIdentifier(ObjectIdentifier[IssuedAccessToken]):
    openapi_title: str = 'Token ID'
    openapi_format: str = 'string'

    @classmethod
    def parse_token(cls, token: str) -> 'IssuedAccessTokenIdentifier':
        return cls(hashlib.md5(str.encode(token, 'utf-8')).hexdigest())