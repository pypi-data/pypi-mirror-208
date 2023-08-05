# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os

import fastapi
from google.cloud import storage


__all__: list[str] = [
    'ApplicationStorageClient'
]


client: storage.Client = storage.Client(project=os.environ['GOOGLE_SERVICE_PROJECT'])


async def get():
    return client


ApplicationStorageClient: storage.Client = fastapi.Depends(get)