# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import Union

import pydantic

from .emailscope import EmailScope
from .genericscope import GenericScope
from .openidscope import OIDCScope
from .profilescope import ProfileScope
from .subscope import SubScope
from .useragentfingerprintscope import UserAgentFingerprint


class GrantedScope(pydantic.BaseModel):
    __root__: Union[
        EmailScope,
        OIDCScope,
        ProfileScope,
        SubScope,
        UserAgentFingerprint,
        GenericScope # IMPORTANT: must be last
    ]

    @property
    def name(self) -> str:
        return self.__root__.name