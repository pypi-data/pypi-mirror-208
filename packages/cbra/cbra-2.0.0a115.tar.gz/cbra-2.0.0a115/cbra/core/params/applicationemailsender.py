# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi

from cbra.types import IEmailSender
from ..ioc import instance


__all__: list[str] = [
    'ApplicationEmailSender'
]


async def get(
    sender: IEmailSender = instance('EmailSender')
) -> IEmailSender:
    return sender


ApplicationEmailSender: IEmailSender = fastapi.Depends(get)