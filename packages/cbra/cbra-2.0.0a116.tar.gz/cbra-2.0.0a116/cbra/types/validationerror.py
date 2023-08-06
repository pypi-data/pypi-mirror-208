# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.


class ValidationError(ValueError):
    """Indicares the validation error on a single scalar or composite
    data element.
    """
    __module__: str = 'cbra.types'
    name: str
    codes: list[str]

    def __init__(self, name: str, codes: list[str]) -> None:
        self.name = name
        self.codes = codes