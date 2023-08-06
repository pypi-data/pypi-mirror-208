# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from collections import defaultdict

from cbra.core.conf import settings
from .staticpermissionsfinder import StaticPermissionsFinder


class SettingsPermissionsFinder(StaticPermissionsFinder): # pragma: no cover
    __module__: str = 'cbra.ext.rbac'
    available: set[str] = set()
    roles: dict[str, set[str]] = defaultdict(set)

    def __init__(self):
        super().__init__(
            available=set(getattr(settings, 'IAM_PERMISSIONS', set())),
            roles={
                role: spec['permissions']
                for role, spec in getattr(settings, 'IAM_ROLES', {}).items()
            }
        )