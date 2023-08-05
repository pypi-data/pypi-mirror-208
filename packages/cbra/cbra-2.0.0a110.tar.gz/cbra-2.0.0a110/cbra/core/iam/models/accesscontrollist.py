# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Any

import pydantic

from cbra.types import PolicyPrincipal


class AccessControlList(pydantic.BaseModel):
    enabled: bool = True
    members: list[PolicyPrincipal] = []

    def is_enabled(self) -> bool:
        """Return a boolean indicating if the ACL is enabled."""
        return self.enabled

    def is_member(self, obj: Any) -> bool:
        """Return a boolean indicating if the object is a member of the
        ACL.
        """
        return any([x.match(obj) for x in self.members])
