# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from .credentialscope import CredentialScope
from .globalcredentialidentifier import GlobalCredentialIdentifier
from .icredentialrepository import CredentialIdentifierType
from .icredentialrepository import ICredentialRepository
from .ipersistablecredential import IPersistableCredential


__all__: list[str] = [
    'CredentialIdentifierType',
    'CredentialScope',
    'GlobalCredentialIdentifier',
    'ICredentialRepository',
    'IPersistableCredential',
]