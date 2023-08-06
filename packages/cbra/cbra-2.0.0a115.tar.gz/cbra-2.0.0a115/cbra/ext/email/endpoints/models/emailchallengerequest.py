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


class EmailChallengeRequest(pydantic.BaseModel):
    email: EmailAddress = pydantic.Field(
        default=...,
        title="Email address",
        description=(
            "The email address to send a verification code to in order to verify "
            "ownership."
        ),
        max_length=320
    )

    def is_request(self) -> bool:
        return True

    def is_solution(self) -> bool:
        return False