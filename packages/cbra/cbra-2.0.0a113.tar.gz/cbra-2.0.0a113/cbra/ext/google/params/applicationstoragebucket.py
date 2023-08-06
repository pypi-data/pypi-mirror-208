# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from datetime import timedelta
from typing import Any

import fastapi
from cbra.core.conf import settings
from google.cloud import storage

from .applicationstorageclient import ApplicationStorageClient


__all__: list[str] = [
    'ApplicationStorageBucket'
]


class StorageBucket:

    def __init__(self, bucket: storage.Bucket) -> None:
        self.bucket = bucket

    async def blob(self, path: str) -> Any:
        obj = self.bucket.blob(path) # type: ignore
        obj.reload() # type: ignore
        return obj

    async def generate_signed_url(
        self,
        path: str,
        expires: timedelta | None = None,
        ttl: int | None = None,
        *args: Any,
        **kwargs: Any
    ) -> str:
        if not bool(ttl) ^ bool(expires):
            raise TypeError("Provider either expires or ttl")
        if ttl is not None:
            expires = timedelta(seconds=ttl)
        blob = self.bucket.blob(path) # type: ignore
        return blob.generate_signed_url( # type: ignore
            expiration=expires,
            *args,
            **kwargs
        )


async def get(client: storage.Client = ApplicationStorageClient) -> storage.Bucket:
    return StorageBucket(client.bucket(settings.APP_STORAGE_BUCKET)) # type: ignore


ApplicationStorageBucket: StorageBucket = fastapi.Depends(get)