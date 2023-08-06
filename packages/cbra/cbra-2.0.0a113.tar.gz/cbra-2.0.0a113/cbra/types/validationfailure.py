# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Iterable

import fastapi

from .abortable import Abortable


class ValidationFailure(Abortable):
    """Indicates the definitive validation failure of the input data for a given
    operation.
    """
    __module__: str = 'cbra.types'
    status_code: int = 422
    errors: dict[str, set[str]]

    def __init__(self, errors: Iterable[tuple[str, Iterable[str]]]) -> None:
        self.errors = {}
        for name, codes in errors:
            if name not in self.errors:
                self.errors[name] = set()
            self.errors[name].update(codes)

    async def as_response(self) -> fastapi.responses.JSONResponse:
        return fastapi.responses.JSONResponse(
            status_code=self.status_code,
            content={
                'errors': {k: list(v) for k, v in self.errors.items()}
            }
        )