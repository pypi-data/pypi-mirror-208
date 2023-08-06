# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from headless.ext.oauth2 import OIDCToken

from .objectidentifier import ObjectIdentifier


class OIDCTokenSubjectIdentifier(ObjectIdentifier[OIDCToken]):
    openapi_title: str = 'OpenID Connect ID Token Subject Identifier'
    openapi_format: str = 'string'