# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import datetime
from typing import Any
from typing import Literal

import pydantic
from canonical import DomainName
from canonical import EmailAddress
from headless.ext.oauth2.models import OIDCToken

from cbra.ext.security import ApplicationKeychain
from cbra.types import ISessionManager
from cbra.types import PersistedModel
from cbra.types import VersionedCipherText
from ..types import PrincipalType
from ..types import SubjectLifecycleType
from .principal import Principal
from .subjectclaimset import SubjectClaimSet


class Subject(PersistedModel):
    kind: Literal['User']
    uid: int | None = pydantic.Field(
        default=None,
        auto_assign=True
    )
    created: datetime
    seen: datetime
    status: SubjectLifecycleType = SubjectLifecycleType.pending

    claims: VersionedCipherText | SubjectClaimSet = pydantic.Field(
        default_factory=SubjectClaimSet
    )

    principals: set[Principal] = set()

    #: TODO: The PeristedModel must be refactored to register attribute mutations
    #: so that the storage backend can detect if it needs to delete something.
    _removed_principals: list[Principal] = pydantic.PrivateAttr([])

    def activate(self) -> None:
        self.status = SubjectLifecycleType.active

    def add_principal(
        self,
        issuer: str,
        value: PrincipalType,
        asserted: datetime,
        trust: bool = False
    ) -> None:
        assert self.uid is not None
        new = Principal.new(self.uid, issuer, value, asserted=asserted, trust=trust)
        old = None
        if new in self.principals:
            # TODO: ugly
            principals = list(self.principals)
            old = principals[principals.index(new)]
        must_add = any([
            old is None,
            old is not None and not old.trust
        ])
        if must_add:
            if old is not None:
                self._removed_principals.append(old)
                self.principals.remove(old)
            self.principals.add(new)

    def add_to_session(self, session: ISessionManager[Any]) -> None:
        raise NotImplementedError
    
    def can_destroy(self) -> bool:
        return self.status == SubjectLifecycleType.pending

    def can_select_email(self) -> bool:
        return len([x for x in self.principals if x.spec.kind == 'EmailAddress']) > 1

    def get_claims(self) -> dict[str, Any]:
        assert isinstance(self.claims, SubjectClaimSet)
        return self.claims.dict(exclude_none=True)

    def get_email(self) -> EmailAddress:
        """Return the oldest email adress of the :class:`Subject`. If the
        :class:`Subject` does not have any email addresses, raise 
        :exc:`ValueError`.
        """
        email: EmailAddress | None = None
        for principal in sorted(self.principals, key=lambda x: x.asserted.timestamp()):
            if principal.spec.kind != 'EmailAddress':
                continue
            email = principal.spec.email
            break
        if email is None:
            raise ValueError("Subject does not have any email address.")
        return email

    def get_principals(self) -> list[Principal]:
        return list([x for x in sorted(self.principals, key=lambda x: x.key)])

    def has_claim(self, claim: str) -> bool:
        assert isinstance(self.claims, SubjectClaimSet)
        return getattr(self.claims, claim, None) is not None

    def has_principal(self, principal: PrincipalType) -> bool:
        p = Principal.new(
            0,
            '',
            principal,
            asserted=datetime.now(),
            trust=False
        )
        return p in self.principals

    def is_active(self) -> bool:
        return self.status == SubjectLifecycleType.active

    def is_encypted(self) -> bool:
        return isinstance(self.claims, VersionedCipherText)

    def merge(self, other: 'Subject') -> None:
        assert self.uid is not None
        assert isinstance(self.claims, SubjectClaimSet)
        assert isinstance(other.claims, SubjectClaimSet)
        for principal in other.principals:
            principal.subject = self.uid
            self.principals.add(principal)

    def needs_fallback_email(self, allow: set[DomainName]) -> bool:
        return not any([
            p.spec.email.domain in allow
            for p in self.principals
            if p.spec.kind == 'EmailAddress'
        ])
    
    def update_oidc(self, oidc: OIDCToken) -> None:
        assert not self.is_encypted()
        assert isinstance(self.claims, SubjectClaimSet)
        self.claims = SubjectClaimSet.parse_obj({
            **oidc.dict(exclude_none=True),
            **self.claims.dict(exclude_none=True)
        })

    def update(self, claims: dict[str, Any], updated_at: datetime) -> None:
        """Update the :class:`Subject` with the given `claims`."""
        assert isinstance(self.claims, SubjectClaimSet)
        self.claims = SubjectClaimSet.parse_obj({
            **self.claims.dict(exclude_none=True),
            **claims,
            'updated_at': int(updated_at.timestamp())
        })
    
    async def decrypt(self, keychain: ApplicationKeychain)  -> None:
        assert isinstance(self.claims, VersionedCipherText), self.claims
        self.claims = await keychain.decrypt(
            self.claims,
            parser=lambda _, pt: SubjectClaimSet.parse_raw(pt)
        )
    
    async def encrypt(self, keychain: ApplicationKeychain)  -> None:
        assert not self.is_encypted()
        self.claims = await keychain.encrypt(self.claims)

    def dict(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        # TODO: A very ugly solution for serialization failure.
        try:
            self.principals = list(self.principals) # type: ignore
            return super().dict(*args, **kwargs)
        finally:
            self.principals = set(self.principals)