# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
from canonical import DomainName


class ClientInfo(pydantic.BaseModel):
    allowed_email_domains: set[DomainName] = set()
    id: str
    client_uri: str | None = None
    contacts: list[str] = []
    logo_uri: str | None = None
    name: str
    organization_name: str
    policy_uri: str | None = None
    sector_identifier: str
    tos_uri: str | None = None