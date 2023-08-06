# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import TypeAlias
from typing import Union

from .applicationclient import ApplicationClient
from .authorizationcodegrant import AuthorizationCodeGrant
from .authorizationrequest import AuthorizationRequest
from .authorizationrequestclient import AuthorizationRequestClient
from .authorizationrequestparameters import AuthorizationRequestParameters
from .authorizationstate import AuthorizationState
from .beginonboardrequest import BeginOnboardRequest
from .beginonboardresponse import BeginOnboardResponse
from .client import Client
from .clientcredentialsgrant import ClientCredentialsGrant
from .currentauthorizationrequest import CurrentAuthorizationRequest
from .externalauthorizationstate import ExternalAuthorizationState
from .frontendloginrequest import FrontendLoginRequest
from .frontendloginresponse import FrontendLoginResponse
from .grant import Grant
from .patchauthorizationrequest import PatchAuthorizationRequest
from .patchauthorizationresponse import PatchAuthorizationResponse
from .resourceowner import ResourceOwner
from .refreshtoken import RefreshToken
from .refreshtokengrant import RefreshTokenGrant
from .sector import Sector
from .managedgrant import ManagedGrant


__all__: list[str] = [
    'ApplicationClient',
    'AuthorizationCodeGrant',
    'AuthorizationRequest',
    'AuthorizationRequestClient',
    'AuthorizationRequestParameters',
    'AuthorizationState',
    'BeginOnboardRequest',
    'BeginOnboardResponse',
    'ClientCredentialsGrant',
    'CurrentAuthorizationRequest',
    'ExternalAuthorizationState',
    'FrontendLoginRequest',
    'FrontendLoginResponse',
    'Grant',
    'ManagedGrant',
    'PatchAuthorizationRequest',
    'PatchAuthorizationResponse',
    'RefreshToken',
    'RefreshTokenGrant',
    'ResourceOwner',
    'Sector',
]


AuthorizationServerModel: TypeAlias = Union[
    AuthorizationRequest,
    AuthorizationRequestParameters,
    AuthorizationState,
    Client,
    Sector
]