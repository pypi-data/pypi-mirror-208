# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import warnings
from typing import Any

from canonical import EmailAddress
from canonical import StringType


class PolicyPrincipal(StringType):
    """Identifies a member (principal) in an access control list or
    role membership. A :class:`PolicyPrincipal` may be one of the following
    types:

    - `domain` - a specific domain. Domain membership is established by
      proving control over an email address for the domain.
    - `user` - a specific user, identified by email address.
    - `sub` - a specific subject, identified by subject identifier.
    """
    __module__: str = 'cbra.types'
    principal_types: set[str] = {
        'domain',
        'user',
        'sub',
    }

    @classmethod
    def validate(cls, v: str) -> str:
        v = super().validate(v)
        t, _ = str.split(v, ':', 1)
        if t not in cls.principal_types:
            raise ValueError(f'invalid principal type: {t}')
        return cls(v)
    
    @functools.singledispatchmethod
    def match(self, obj: Any) -> bool:
        warnings.warn(
            f"Unknown princpal for access policy: {type(obj).__name__}"
        )
        return False
    
    @match.register
    def match_email(self, email: EmailAddress) -> bool:
        kind, value = str.split(self, ':', 1)
        if kind not in {'domain', 'user', 'sub'}:
            return False
        is_matching = False
        if kind == 'domain':
            is_matching = value == str(email.domain)
        elif kind == 'user':
            is_matching = value == str(email)
        return is_matching
