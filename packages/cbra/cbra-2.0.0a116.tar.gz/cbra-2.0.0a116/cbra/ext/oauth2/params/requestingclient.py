# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import secrets

import fastapi
from headless.ext.oauth2 import ClientAssertionType
from ckms.core.models import JOSEObject
from ckms.core.models import JSONWebSignature

import cbra.core as cbra
from cbra.types import Request
from ..authorizationserverstorage import AuthorizationServerStorage
from ..models import Client
from ..types import ClientAuthenticationMethod
from ..types import FatalClientException
from ..types import InvalidClient
from ..types import InvalidRequest


__all__: list[str] = [
    'RequestingClient'
]


MAX_CLIENT_ASSERTION_AGE: int = 60


async def get_from_client_assertion(
    request: Request,
    storage: AuthorizationServerStorage,
    assertion_type: ClientAssertionType | None,
    assertion: str,
) -> Client:
    if not assertion_type:
        raise InvalidRequest("The 'assertion_type' parameter is required.")
    if assertion_type != ClientAssertionType.jwt_bearer:
        raise InvalidRequest(f"Unsupported assertion type: {assertion_type[:64]}")
    try:
        jws = JOSEObject.parse(assertion)
    except Exception:
        raise InvalidClient("Unable to decode the JWT client assertion.")
    if not isinstance(jws, JSONWebSignature):
        raise InvalidClient(
            "The JOSE object in the client assertion must be of type "
            "JSON Web Signature (JWS)."
        )
    if str.lower(jws.typ or '') != 'jwt':
        raise InvalidClient(
            message=(
                "A JSON Web Token (JWT) enclosed in the assertion must be of "
                "type 'JWT'."
            )
        )
    try:
        jwt = jws.claims(accept={'jwt'})
    except Exception:
        raise InvalidClient("Unable to deserialize the JWT as JSON.")
    try:
        jwt.verify(
            audience={str(request.url)},
            max_age=MAX_CLIENT_ASSERTION_AGE
        )
    except Exception:
        raise InvalidClient(
            "The JSON Web Token (JWT) had an invalid audience, was "
            "expired or not effective, or otherwise did not satisfy "
            "the requirements specified in RFC 7523."
        )
    if jwt.iss != jwt.sub:
        raise InvalidClient(
            "The JSON Web Token (JWT) must be issued by the "
            "client."
        )

    client = await storage.get(Client, jwt.iss)
    if client is None:
        raise InvalidClient('The client does not exist.')
    if client.auth_method != ClientAuthenticationMethod.private_key:
        raise InvalidClient(
            "The client does not allow the provided authentication mode."
        )
    if client.jwks is None:
        raise InvalidClient(
            "No known keys could verify the signature of the JWS."
        )
    if not await jws.verify(client.jwks):
        raise InvalidClient(
            "No signatures in the JSON Web Signature (JWS) could "
            "be verified using the known keys of the client."
        )
    return client


async def get(
    request: Request,
    storage: AuthorizationServerStorage = cbra.instance('_AuthorizationServerStorage'),
    client_id: str | None = fastapi.Form(
        default=None,
        title="Client ID",
        description=(
            "**Required**, if the client is not authenticating with the "
            "authorization server or the chosen method of authentication is "
            "`client_secret_post`, `client_secret_jwt`, or `private_key_jwt`, "
            "otherwise this parameter is ignored."
        )
    ),
    client_secret: str | None = fastapi.Form(
        default=None,
        title="Client secret",
        description=(
            "The client-side secret. **Required** if the client is confidential and "
            "authenticates using `client_secret_post`."
        )
    ),
    assertion: str | None = fastapi.Form(
        default=None,
        title="Client assertion",
        alias='client_assertion',
        description=(
            "A digitally signed artifact that was created using a pre-registered "
            "asymmetric keypair. The `client_assertion_type` indicates the format "
            "and protocol used to create the assertion."
        )
    ),
    assertion_type: ClientAssertionType | None = fastapi.Form(
        default=None,
        title="Client assertion type",
        alias='client_assertion_type',
        description="The assertion type used by the client."
    )
) -> Client:
    if assertion is not None:
        return await get_from_client_assertion(request, storage, assertion_type, assertion)
    if client_id is None:
        raise InvalidClient
    client = await storage.get(Client, client_id)
    if client is None:
        raise FatalClientException(
            code='invalid_client',
            message='The client does not exist.'
        )
    if client.auth_method != ClientAuthenticationMethod.post:
        raise NotImplementedError
    # TODO: This is highly specific for client_secret_post
    if client.is_confidential() and not client_secret:
        raise FatalClientException(
            code='invalid_client',
            message="The 'client_secret' parameter is mandatory for this client."
        )
    secret = await client.get_client_secret()
    if not secrets.compare_digest(secret or '', client_secret or ''):
        raise FatalClientException(
            code='invalid_client',
            message="The provided client secret is not valid."
        )

    return client


RequestingClient: Client = fastapi.Depends(get)