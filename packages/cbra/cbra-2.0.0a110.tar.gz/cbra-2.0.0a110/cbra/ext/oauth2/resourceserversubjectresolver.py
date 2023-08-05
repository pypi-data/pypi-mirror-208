# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra.core.conf import settings
from cbra.ext import cache
from cbra.types import ICache
from cbra.types import ISubject
from cbra.types import ISubjectResolver
from .resource.types import UserInfoSubject
from .params import RequestAccessToken


class ResourceServerSubjectResolver(ISubjectResolver):
    __module__: str = 'cbra.ext.oauth2'
    storage: ICache

    def __init__(
        self,
        storage: ICache = cache.cache(settings.OAUTH2_CACHE)
    ):
        self.storage = storage

    def cache_key(self, principal: RequestAccessToken):
        return f'oauth2:access-token:userinfo:{principal.token_id}'

    async def resolve( # type: ignore
        self,
        principal: RequestAccessToken
    ) -> ISubject:
        assert principal.token_id is not None
        userinfo = await self.storage.get(self.cache_key(principal))
        if userinfo is None:
            userinfo = await principal.userinfo()
            await self.storage.set(self.cache_key(principal), userinfo.dict())
        return UserInfoSubject(userinfo)