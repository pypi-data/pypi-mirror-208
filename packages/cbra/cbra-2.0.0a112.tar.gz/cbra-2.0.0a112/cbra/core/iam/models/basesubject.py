# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import datetime
from typing import Literal

import pydantic

from cbra.types import PersistedModel
from ..types import SubjectLifecycleType


class BaseSubject(PersistedModel):
    kind: Literal['User']
    uid: int | None = pydantic.Field(
        default=None,
        auto_assign=True
    )
    created: datetime
    seen: datetime
    status: SubjectLifecycleType = SubjectLifecycleType.pending

    def is_encypted(self) -> bool:
        raise NotImplementedError