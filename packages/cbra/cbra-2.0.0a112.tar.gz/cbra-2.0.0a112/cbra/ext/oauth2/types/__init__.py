# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from headless.ext.oauth2.types import ResponseType

from .accesstype import AccessType
from .authorizeresponse import AuthorizeResponse
from .authorizationcode import AuthorizationCode
from .authorizationlifecycle import AuthorizationLifecycle
from .authorizationrequestidentifier import AuthorizationRequestIdentifier
from .authorizationstate import AuthorizationState
from .authorizationstateidentifier import AuthorizationStateIdentifier
from .bearertoken import BearerToken
from .bearertokencredential import BearerTokenCredential
from .bearertokenexception import BearerTokenException
from .clientauthenticationmethod import ClientAuthenticationMethod
from .clientidentifier import ClientIdentifier
from .clientinfo import ClientInfo
from .compositeobjectidentifier import CompositeObjectIdentifier
from .extauthorizationrequeststate import ExtAuthorizationRequestState
from .frontendexception import FrontendException
from .frontendobjecttype import FrontendObjectType
from .grantedscope import GrantedScope
from .iaccesstoken import IAccessToken
from .iaccesstokenobtainer import IAccessTokenObtainer
from .iauthorizationserverstorage import IAuthorizationServerStorage
from .fatalauthorizationexception import FatalAuthorizationException
from .fatalclientexception import FatalClientException
from .iauthorizationrequest import IAuthorizationRequest
from .invalidgrant import InvalidGrant
from .invalidtarget import InvalidTarget
from .iclient import IClient
from .iexternalauthorizationstate import IExternalAuthorizationState
from .ifrontendstorage import IFrontendStorage
from .imanagedgrant import IManagedGrant
from .invalidclient import InvalidClient
from .invalidrequest import InvalidRequest
from .invalidresponsetype import InvalidResponseTypeRequested
from .invalidscope import InvalidScope
from .irefreshtoken import IRefreshToken
from .iresourceowner import IResourceOwner
from .iresourceserverstorage import IResourceServerStorage
from .issuedaccesstoken import IssuedAccessToken
from .issuedaccesstokenidentifier import IssuedAccessTokenIdentifier
from .itokenbuilder import ITokenBuilder
from .itokensigner import ITokenSigner
from .jarmauthorizeresponse import JARMAuthorizeResponse
from .queryauthorizeresponse import QueryAuthorizeResponse
from .loginresponse import LoginResponse
from .managedgrantidentifier import ManagedGrantIdentifier
from .missingresponsetype import MissingResponseType
from .norefreshtokenreturned import NoRefreshTokenReturned
from .objectidentifier import ObjectIdentifier
from .oidcclaimset import OIDCClaimSet
from .oidcprovider import OIDCProvider
from .oidctokensubjectidentifier import OIDCTokenSubjectIdentifier
from .pairwiseidentifier import PairwiseIdentifier
from .principalidentifier import PrincipalIdentifier
from .prompttype import PromptType
from .redirecturi import RedirectURI
from .redirectparameters import RedirectParameters
from .refreshtokenidentifier import RefreshTokenIdentifier
from .refreshtokenpolicytype import RefreshTokenPolicyType
from .refreshtokentype import RefreshTokenType
from .requestedscope import RequestedScope
from .resourceaccesstokenidentifier import ResourceAccessTokenIdentifier
from .resourceserveraccesstoken import ResourceServerAccessToken
from .resourceowneridentifier import ResourceOwnerIdentifier
from .responsemodenotsupported import ResponseModeNotSupported
from .responsevalidationfailure import ResponseValidationFailure
from .rfc9068accesstoken import RFC9068AccessToken
from .signableoidctoken import SignableOIDCToken
from .unsupportedauthorizationresponse import UnsupportedAuthorizationResponse
from .usererror import UserError


__all__: list[str] = [
    'AccessType',
    'AuthorizeResponse',
    'AuthorizationCode',
    'AuthorizationLifecycle',
    'AuthorizationRequestIdentifier',
    'AuthorizationState',
    'AuthorizationStateIdentifier',
    'BearerToken',
    'BearerTokenCredential',
    'BearerTokenException',
    'ClientIdentifier',
    'ClientInfo',
    'ClientAuthenticationMethod',
    'CompositeObjectIdentifier',
    'ExtAuthorizationRequestState',
    'FatalAuthorizationException',
    'FatalClientException',
    'FrontendException',
    'FrontendObjectType',
    'GrantedScope',
    'IAccessToken',
    'IAccessTokenObtainer',
    'IAuthorizationRequest',
    'IAuthorizationServerStorage',
    'IClient',
    'IExternalAuthorizationState',
    'IFrontendStorage',
    'IManagedGrant',
    'InvalidClient',
    'InvalidGrant',
    'InvalidRequest',
    'InvalidScope',
    'InvalidTarget',
    'InvalidResponseTypeRequested',
    'IRefreshToken',
    'IResourceOwner',
    'IResourceServerStorage',
    'IssuedAccessToken',
    'IssuedAccessTokenIdentifier',
    'ITokenBuilder',
    'ITokenSigner',
    'JARMAuthorizeResponse',
    'LoginResponse',
    'ManagedGrantIdentifier',
    'MissingResponseType',
    'NoRefreshTokenReturned',
    'ObjectIdentifier',
    'OIDCClaimSet',
    'OIDCProvider',
    'OIDCTokenSubjectIdentifier',
    'PairwiseIdentifier',
    'PrincipalIdentifier',
    'PromptType',
    'QueryAuthorizeResponse',
    'RedirectURI',
    'RedirectParameters',
    'RefreshTokenIdentifier',
    'RefreshTokenPolicyType',
    'RefreshTokenType',
    'RequestedScope',
    'ResourceAccessTokenIdentifier',
    'ResourceOwnerIdentifier',
    'ResourceServerAccessToken',
    'ResponseModeNotSupported',
    'ResponseType',
    'ResponseValidationFailure',
    'RFC9068AccessToken',
    'SignableOIDCToken',
    'UnsupportedAuthorizationResponse',
    'UserError',
]