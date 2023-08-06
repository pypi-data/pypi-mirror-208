# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic

from cbra.core.iam.models import SubjectClaimSet

from .mailbox import Mailbox


class CurrentSubjectResponse(SubjectClaimSet):
    sub: str = pydantic.Field(
        default=...
    )

    mailboxes: list[Mailbox] = pydantic.Field(
        default=[],
        title="Mailboxes",
        description="The list of available mailboxes."
    )