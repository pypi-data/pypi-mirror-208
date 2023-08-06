# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic
from canonical import EmailAddress


class Mailbox(pydantic.BaseModel):
    principal_id: str = pydantic.Field(
        default=...,
        title="Principal ID",
        description="The principal identifying the mailbox."
    )

    email: EmailAddress = pydantic.Field(
        default=...,
        title="Email",
        description=(
            "An email address that a Subject may use to sign in."
        )
    )