# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import json
from typing import Any
from typing import TypeVar

import pydantic
from google.cloud.datastore import Client as GoogleClient

import cbra.core as cbra
from cbra.ext.google.types import IDatastoreEntity
from cbra.ext.google.types import IDatastoreKey
from cbra.ext.google import BaseDatastoreRepository
from cbra.ext.security import ApplicationKeychain


T = TypeVar('T', bound=pydantic.BaseModel)


class BaseModelStorage(BaseDatastoreRepository):
    keychain: ApplicationKeychain

    def __init__(
        self,
        client: GoogleClient | Any = cbra.inject('GoogleDatastoreClient'),
        keychain: ApplicationKeychain = ApplicationKeychain.depends()
    ):
        if not isinstance(client, GoogleClient):
            raise TypeError(f"Invalid client: {repr(client)}")
        self.client = client
        self.keychain = keychain

    def entity_to_model(
        self,
        cls: type[T],
        entity: IDatastoreEntity | None,
        **kwargs: Any
    ) -> T | None:
        if entity is None:
            return None
        return cls.parse_obj({**dict(entity), **kwargs}) # type: ignore

    def model_to_entity(
        self,
        key: IDatastoreKey,
        obj: pydantic.BaseModel,
        exclude: set[str] | None = None,
        exclude_none: bool = False
    ) -> IDatastoreEntity:
        # TODO: this is only here to prevent encoding issues with protobuf
        entity = self.entity_factory(key)
        entity.update(json.loads(obj.json(exclude=exclude, exclude_none=exclude_none)))
        return entity