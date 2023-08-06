# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any
from typing import Union

import pydantic

from cbra.core.iam.models import Subject
from .emailscope import EmailScope
from .genericscope import GenericScope
from .iauthorizationrequest import IAuthorizationRequest
from .iresourceowner import IResourceOwner
from .openidscope import OIDCScope
from .profilescope import ProfileScope
from .subscope import SubScope
from .useragentfingerprintscope import UserAgentFingerprint


class RequestedScope(pydantic.BaseModel):
    __root__: Union[
        EmailScope,
        OIDCScope,
        ProfileScope,
        SubScope,
        UserAgentFingerprint,
        GenericScope # IMPORTANT: this needs to be last
    ]

    @property
    def name(self) -> str:
        return self.__root__.name

    @pydantic.root_validator(pre=True) # type: ignore
    def preprocess(cls, values: dict[str, Any]) -> dict[str, Any]:
        root: dict[str, Any] | str | None = values.get('__root__')
        if isinstance(root, str):
            values['__root__'] = root = {'name': root}
        return values

    def apply(
        self,
        subject: Subject,
        owner: IResourceOwner,
        claims: dict[str, Any],
        request: IAuthorizationRequest | None = None
    ) -> None:
        return self.__root__.apply(
            subject=subject,
            owner=owner,
            claims=claims,
            request=request
        )
    
    def requires_consent(self) -> bool:
        return self.__root__.requires_consent()

    def wants(self) -> tuple[set[str], set[str]]:
        """Return a tuple containing two sets of strings, where the
        first set contains the claims that a :term:`Subject` is
        required to have to satify this scope, and the second contains
        optional claims. The default implementation returns a tuple
        holding two empty sets
        """
        required, optional = self.__root__.wants()

        # TODO: This is a hack, but we need to ensure that a Subject has a given_name
        # and family_name in order to have any meaning for name_order.
        if 'name_order' in required:
            required.add("given_name")
            required.add("family_name")
        if 'given_name' in required:
            required.add('nickname')
        return required, optional - required

    def __str__(self) -> str:
        return self.name