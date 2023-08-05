# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Iterable


class Scope:
    """Represents the scope required to access an endpoint or resource."""
    __module__: str = 'cbra.ext.oauth2.resource.types'
    requires: set[str]

    def __init__(self, scope: str | Iterable[str]):
        if isinstance(scope, str):
            scope = [scope]
        self.requires = set(scope)

    def missing(self, granted: set[str]) -> set[str]:
        """Return the set containing the scope that is missing."""
        return self.requires - granted