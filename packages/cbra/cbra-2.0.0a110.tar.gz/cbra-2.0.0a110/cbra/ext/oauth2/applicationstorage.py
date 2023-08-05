# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os
import pathlib
from typing import Any
from typing import TypeVar

import jinja2
import yaml

from cbra.core.conf import settings
from cbra.types import Request
from .basestorage import BaseStorage
from .models import AuthorizationServerModel
from .models import Client
from .types import ClientIdentifier
from .types import ObjectIdentifier
from .types import PrincipalIdentifier


T = TypeVar('T', bound=AuthorizationServerModel)


class ApplicationStorage(BaseStorage):
    """A :class:`~cbra.ext.oauth2.BaseStorage` implementation that
    retrieves specific resources from either environment variables,
    local configuration files, or the :mod:`~cbra.core.conf.settings`
    module.
    """
    __module__: str = 'cbra.ext.oauth2'
    clients: dict[str, pathlib.Path | Client]
    client_config_dir: pathlib.Path
    template: jinja2.Environment = jinja2.Environment(
        variable_start_string='${',
        variable_end_string='}'
    )

    def __init__(
        self,
        request: Request,
    ) -> None:
        self.client_config_dir = pathlib.Path(settings.OAUTH2_CLIENT_CONFIG_DIR)
        self.clients = {
            x.with_suffix('').name: x
            for x in self.client_config_dir.glob('**/*.yml')
        }

    async def fetch(self, oid: ObjectIdentifier[T]) -> T | None:
        if isinstance(oid, ClientIdentifier):
            return await super().get(Client, str(oid)) # type: ignore
        else:
            return None

    async def get(self, cls: type[T], *args: Any, **kwargs: Any) -> T | None:
        if cls == Client:
            return await super().get(cls, *args, **kwargs)
        else:
            return None
        
    async def get_client(self, client_id: str) -> Client | None:
        client = self.clients.get(client_id)
        if client is not None and not isinstance(client, Client):
            assert isinstance(client, pathlib.Path)
            with open(client) as f:
                client = await self.load_client_config_file(client_id, f.read())
        return client

    async def load_client_config_file(self, client_id: str, content: str) -> Client:
        t = self.template.from_string(content)
        c = {'env': os.environ, 'settings': settings}
        return Client.parse_obj({
            **yaml.safe_load(t.render(c)), # type: ignore
            'client_id': client_id
        })