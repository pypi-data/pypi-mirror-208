# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import pydantic


class EmailChallengeSolutionResponse(pydantic.BaseModel):
    success: bool = pydantic.Field(
        default=...,
        title="Success?",
        description=(
            "Indicates if the attempt to solve the challenge was successful."
        )
    )

    blocked: bool = pydantic.Field(
        default=...,
        title="Blocked?",
        description=(
            "Indicates if the challenge is blocked or otherwise invalid, and the "
            "client must obtain a new challenge to resolve."
        )
    )