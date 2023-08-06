# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import TypeVar

import pydantic
from headless.ext.oauth2.models import TokenResponse


T = TypeVar('T', bound='BearerToken')


class BearerToken(pydantic.BaseModel):
    access_token: str
    expires: datetime

    @classmethod
    def parse_token_response(
        cls: type[T],
        response: TokenResponse,
        leeway: int = 30
    ) -> T:
        return cls.parse_obj({
            'access_token': str(response.access_token),
            'expires': datetime.now(timezone.utc)\
                + timedelta(seconds=response.expires_in - leeway)
        })

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires
    
    def __str__(self) -> str:
        return self.access_token