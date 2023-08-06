# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import functools
import inspect
from typing import Any
from typing import Coroutine
from typing import Callable
from typing import TypeVar

from .memorysecret import MemorySecret
from .secret import Secret


__all__: list[str] = ['Secret', 'parse', 'register']

T = TypeVar('T', bound='Secret')

__providers: dict[str, type[Secret]] = {
    'memory': MemorySecret
}


def parse(provider: str, **params: Any) -> Secret:
    if provider not in __providers:
        raise ValueError(f'unknown secret provider: {provider}')
    return __providers[provider].parse_obj({'provider': provider, **params})


@functools.singledispatch
async def load(obj: T) -> T:
    raise TypeError(type(obj).__name__)


def register(provider: str, func: Callable[[T], Coroutine[Any, Any, T]]) -> None:
    sig = inspect.signature(func)
    p = sig.parameters.get('secret')
    if p is None:
        raise TypeError(f'{func.__name__} must accept the \'secret\' parameter.')
    if p.annotation == type(inspect.Parameter.empty())\
    or not inspect.isclass(p.annotation)\
    or not issubclass(p.annotation, Secret):
        raise TypeError(
            "The \'secret\' argument must be annotated with a subclass of "
            "cbra.ext.secrets.Secret"
        )
    load.register(func) # type: ignore
    __providers[provider] = p.annotation