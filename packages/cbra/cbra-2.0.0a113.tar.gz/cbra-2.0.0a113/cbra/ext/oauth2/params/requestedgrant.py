# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging
import re

import fastapi
import pydantic
from headless.ext.oauth2.types import GrantType

import cbra.core as cbra
from cbra.core.iam.types import Subject
from ..authorizationserverstorage import AuthorizationServerStorage
from ..models import Client
from ..models import Grant
from ..models import ResourceOwner
from ..types import AuthorizationCode
from ..types import FatalClientException
from ..types import IAuthorizationRequest
from ..types import InvalidRequest
from ..types import RefreshTokenIdentifier
from .requestingclient import RequestingClient


logger: logging.Logger = logging.getLogger('cbra.endpoint')


async def get(
    storage: AuthorizationServerStorage = cbra.instance('_AuthorizationServerStorage'),
    client: Client = RequestingClient,
    grant_type: str = fastapi.Form(
        default=...,
        title="Grant type"
    ),
    code: AuthorizationCode | None = fastapi.Form(
        default=None,
        title="Code",
        description=(
            "The authorization code received from the authorization server. "
            "This parameter is **required** when `grant_type` is "
            "`authorization_code`, otherwise it is ignored."
        )
    ),
    redirect_uri: str | None = fastapi.Form(
        default=None,
        title="Redirect URI",
        description=(
            "This parameter is **required**, if the `redirect_uri` parameter "
            "was included in the authorization request, in which case their "
            "values **must"" be identical.  If no `redirect_uri` was included "
            "in the authorization request, this parameter is **optional**."
        )
    ),
    refresh_token: RefreshTokenIdentifier | None = fastapi.Form(
        default=None,
        title="Refresh token",
        description=(
            "The refresh token issued to the client. This parameter is "
            "**required** if `grant_type` is `refresh_token`."
        )
    ),
    resource: str | None = fastapi.Form(
        default=None,
        title="Resource",
        description=(
            "Indicates the target service or protected resource where the "
            "client intends to use the requested access token."
        )
    ),
    scope: str | None = fastapi.Form(
        default=None,
        title="Scope",
        description=(
            "The scope of the access request. "
            "The requested scope MUST NOT include any scope not "
            "originally granted by the resource owner, and if "
            "omitted is treated as equal to the scope originally "
            "granted by the resource owner."
        )
    )
):
    try:
        grant_type = GrantType(grant_type)
    except ValueError:
        raise FatalClientException(
            code='unsupported_grant_type',
            message=(
                "The authorization server does not support the given grant:"
                f"{grant_type[:64]}"
            )
        )
    if not client.can_grant(grant_type):
        raise FatalClientException(
            code='unauthorized_client',
            message=(
                "The client does not allow or is not allowed to use the "
                f"given grant: {grant_type[:64]}"
            )
        )
    
    authnrequest: IAuthorizationRequest | None = None
    owner: ResourceOwner | None = None
    subject: Subject | None = None
    if grant_type == GrantType.authorization_code:
        if code is None:
            raise InvalidRequest("The authorization code is not accepted by the server.")
        authnrequest = await storage.fetch(code)
    if authnrequest is not None:
        assert authnrequest.has_owner()
        owner = await storage.get(ResourceOwner, authnrequest.owner)
        subject = await storage.get(Subject, authnrequest.owner.sub)
    if owner is None:
        logger.critical("Resource owner not found (client: %s)", client.client_id)
    if subject is None:
        logger.critical("Subject not found (client: %s)", client.client_id)
    try:
        return Grant.parse_obj({
            'grant_type': grant_type,
            'code': code,
            'client': client,
            'owner': owner,
            'redirect_uri': redirect_uri,
            'refresh_token': refresh_token,
            'resource': resource,
            'request': authnrequest,
            'scope': set(filter(bool, re.split(r'\s+', scope or ''))),
            'subject': subject
        })
    except pydantic.ValidationError as e:
        logger.debug("Caught fatal ValidationError: %s", repr(e))
        raise InvalidRequest(
            f"The parameters for grant {grant_type[:64]} were invalid, "
            f"incomplete, duplicated or otherwise malformed."
        )


RequestedGrant: Grant = fastapi.Depends(get)