# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from cbra.ext.email import EmailChallengeEndpoint


class EmailRegistrationEndpoint(EmailChallengeEndpoint):
    __module__: str = 'cbra.ext.oauth2.server'
    name: str = 'oauth2.register.email'
    path_name: str = 'email'
    path: str = '/register/email'
    summary: str = 'Email Registration Endpoint'