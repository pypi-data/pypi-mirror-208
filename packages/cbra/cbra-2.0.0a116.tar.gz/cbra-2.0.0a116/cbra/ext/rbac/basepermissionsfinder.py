# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


class BasePermissionsFinder:
    """Exposes an interface to determine permissions for a given role."""
    __module__: str = 'cbra.ext.rbac'

    async def get(self, roles: set[str]) -> set[str]:
        """Return the set of permissions granted to the given role."""
        raise NotImplementedError