# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import operator
import re
from collections import defaultdict

from .basepermissionsfinder import BasePermissionsFinder


class StaticPermissionsFinder(BasePermissionsFinder):
    __module__: str = 'cbra.ext.rbac'
    available: set[str] = set()
    roles: dict[str, set[str]] = defaultdict(set)

    def __init__(self, available: set[str], roles: dict[str, set[str]]):
        self.available = available
        self.roles = roles

    async def get(self, roles: set[str]) -> set[str]:
        """Return the set of permissions granted to the given roles."""
        permissions: set[str] = functools.reduce(
            operator.or_,
            [self.roles.get(x) or set() for x in roles],
            set()
        )
        for permission in list(permissions):
            if '*' not in permission:
                continue
            pattern = re.compile(re.escape(permission).replace('\\*', '[a-z]+'))
            permissions.remove(permission)
            permissions.update({x for x in self.available if pattern.match(x)})
        return permissions
