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


class EmailChallengeSolutionRequest(pydantic.BaseModel):
    challenge_id: str = pydantic.Field(
        default=...,
        title="Challenge ID",
        alias='challengeId',
        description=(
            "The challenge identifier that was obtained when creating the "
            "challenge."
        ),
        max_length=64
    )

    email: EmailAddress = pydantic.Field(
        default=...,
        title="Email address",
        description=(
            "The email address to which the challenge was sent."
        ),
        editable=False,
        max_length=320
    )

    code: str = pydantic.Field(
        default=...,
        title="Code",
        description=(
            "The verification code that was sent to the email address, or "
            "another solution that proves the ownership of the email address."
        ),
        max_length=10
    )

    def is_request(self) -> bool:
        return False

    def is_solution(self) -> bool:
        return True