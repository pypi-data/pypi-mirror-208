# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi


class Abortable(Exception):
    """An exception class that is detected by the framework and
    can be converted for a corresponding HTTP response.

    Be aware that any part of the code that catches an :class:`Abortable`
    is allowed to abort the operation in progress and return a response
    to the client.
    """
    __module__: str = 'cbra.types'
    headers: dict[str, str]
    status_code: int = 500

    def __init__(self, headers: dict[str, str] | None = None) -> None:
        self.headers = headers or {}

    async def as_response(self) -> fastapi.Response:
        return fastapi.Response(
            headers=self.headers,
            status_code=self.status_code
        )