# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import re
from typing import Any
from typing import TypeVar

from headless.ext.oauth2 import OIDCToken
from headless.ext.oauth2.models import SubjectIdentifier

from cbra.core.iam.models import Subject
from cbra.types import IDependant
from .models import AuthorizationServerModel
from .models import AuthorizationRequest
from .models import AuthorizationRequestParameters
from .models import AuthorizationState
from .models import ExternalAuthorizationState
from .models import Client
from .models import ManagedGrant
from .models import RefreshToken
from .models import ResourceOwner
from .types import AuthorizationCode
from .types import AuthorizationRequestIdentifier
from .types import IssuedAccessToken
from .types import ObjectIdentifier
from .types import PairwiseIdentifier


T = TypeVar('T', bound=Any)


class BaseStorage(IDependant):
    __module__: str = 'cbra.ext.oauth2'
    pattern: re.Pattern[str] = re.compile(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

    async def destroy(self, obj: AuthorizationServerModel) -> None:
        raise NotImplementedError

    async def fetch(self, key: ObjectIdentifier[T]) -> None | T:
        raise NotImplementedError

    async def get_oidc_token(self, oid: SubjectIdentifier) -> OIDCToken | None:
        raise NotImplementedError

    # TODO: Refactor everything below this line.
    async def get(
        self,
        cls: type[T],
        *args: Any,
        **kwargs: Any
    ) -> T | None:
        name = self.pattern.sub(r'_\1', cls.__name__)
        fn = f"get_{str.lower(name)}"
        if not hasattr(self, fn):
            raise NotImplementedError(
                f'{type(self).__name__}.{fn}() is not implemented.'
            )
        return await getattr(self, fn)(*args, **kwargs)

    async def get_authorization_request(
        self,
        oid: AuthorizationCode | AuthorizationRequestIdentifier
    ) -> AuthorizationRequest | None:
        params = await self.get(AuthorizationRequestParameters, oid)
        if params is None:
            return None
        return AuthorizationRequest.parse_obj(params)

    @functools.singledispatchmethod
    async def get_authorization_request_parameters(
        self,
        oid: AuthorizationCode | str
    ) -> AuthorizationRequestParameters | None:
        raise NotImplementedError(repr(oid))
    
    @get_authorization_request_parameters.register
    async def _get_authorization_request_by_code(
        self,
        oid: AuthorizationCode
    ) -> AuthorizationRequestParameters | None:
        return await self.get_authorization_request_by_code(oid)
    
    @get_authorization_request_parameters.register
    async def _get_authorization_request_by_id(
        self,
        oid: AuthorizationRequestIdentifier
    ) -> AuthorizationRequestParameters | None:
        return await self.get_authorization_request_by_id(oid)

    async def get_authorization_request_by_code(
        self,
        oid: AuthorizationCode
    ) -> AuthorizationRequestParameters | None: 
        raise NotImplementedError

    async def get_authorization_request_by_id(
        self,
        oid: AuthorizationRequestIdentifier
    ) -> AuthorizationRequestParameters | None: 
        raise NotImplementedError

    async def get_state(self, key: str) -> AuthorizationState | None:
        raise NotImplementedError

    @functools.singledispatchmethod
    async def persist(
        self,
        obj: AuthorizationServerModel | Subject
    ) -> None:
        raise TypeError(type(obj).__name__)

    async def persist_authorization_request(
        self,
        obj: AuthorizationRequestParameters
    ) -> None:
        raise NotImplementedError

    async def persist_client(self, obj: Client) -> None:
        raise NotImplementedError

    async def persist_issued_access_token(
        self,
        obj: IssuedAccessToken
    ) -> None:
        raise NotImplementedError

    async def persist_managed_grant(
        self,
        obj: ManagedGrant
    ) -> None:
        raise NotImplementedError

    async def persist_oidc_token(self, obj: OIDCToken) -> None:
        raise NotImplementedError

    async def persist_ppid(self, obj: PairwiseIdentifier) -> None:
        raise NotImplementedError

    async def persist_refresh_token(
        self,
        obj: RefreshToken
    ) -> None:
            raise NotImplementedError

    async def persist_resource_owner(self, obj: ResourceOwner) -> None:
        raise NotImplementedError

    async def persist_state(self, obj: AuthorizationState | ExternalAuthorizationState) -> None:
        raise NotImplementedError
    
    async def persist_subject(self, obj: Subject) -> None:
        raise NotImplementedError

    @persist.register
    async def _persist_authorization_request(
        self,
        obj: AuthorizationRequestParameters
    ) -> None:
        return await self.persist_authorization_request(obj)

    @persist.register
    async def _persist_client(
        self,
        obj: Client
    ) -> None:
        return await self.persist_client(obj)

    @persist.register
    async def _persist_external_state(
        self,
        obj: ExternalAuthorizationState
    ) -> None:
        return await self.persist_state(obj)

    @persist.register
    async def _persist_issued_access_token(
        self,
        obj: IssuedAccessToken
    ) -> None:
        return await self.persist_issued_access_token(obj)

    @persist.register
    async def _persist_managed_grant(
        self,
        obj: ManagedGrant
    ) -> None:
        return await self.persist_managed_grant(obj)

    @persist.register
    async def _persist_oidc_token(self, obj: OIDCToken) -> None:
        return await self.persist_oidc_token(obj)

    @persist.register
    async def _persist_ppid(
        self,
        obj: PairwiseIdentifier
    ) -> None:
        return await self.persist_ppid(obj)

    @persist.register
    async def _persist_refresh_token(
        self,
        obj: RefreshToken
    ) -> None:
        return await self.persist_refresh_token(obj)

    @persist.register
    async def _persist_resource_owner(
        self,
        obj: ResourceOwner
    ) -> None:
        return await self.persist_resource_owner(obj)

    @persist.register
    async def _persist_state(
        self,
        obj: AuthorizationState
    ) -> None:
        return await self.persist_state(obj)

    @persist.register
    async def _persist_subject(
        self,
        obj: Subject
    ) -> None:
        return await self.persist_subject(obj)