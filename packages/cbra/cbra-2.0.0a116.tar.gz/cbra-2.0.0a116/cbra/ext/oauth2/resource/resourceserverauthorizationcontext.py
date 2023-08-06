# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast

from cbra.types import IAuthorizationContext
from cbra.types import ISubject
from cbra.types import Request
from .types import UserInfoSubject


class ResourceServerAuthorizationContext(IAuthorizationContext):
    __module__: str = 'cbra.ext.oauth2.resource'
    _request: Request
    _subject: UserInfoSubject

    def __init__(
        self,
        request: Request,
        subject: ISubject
    ):
        self._request = request
        self._subject = cast(UserInfoSubject, subject)

    def get_subject(self) -> ISubject:
        return self._subject