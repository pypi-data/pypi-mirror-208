# Copyright (C) 2022 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os
from typing import Any
os.environ['PYTHON_SETTINGS_MODULE'] = __name__

import uvicorn

from cbra.ext import oauth2
from cbra.ext.google import Service


APP_ISSUER: str = 'https://localhost.webiam.id'

APP_CLIENT_ID: str = 'self'

APP_CLIENT_SECRET = SECRET_KEY = 'changeme'

DEBUG: bool = True

OAUTH2_CLIENTS: list[dict[str, Any]] = [
    {
        'name': "google",
        'issuer': 'https://accounts.google.com',
        'allowed_email_domains': ['gmail.com'],
        'credential': {
            'kind': 'ClientSecret',
            'client_id': os.environ['WEBID_GOOGLE_CLIENT_ID'],
            'client_secret': os.environ['WEBID_GOOGLE_CLIENT_SECRET']
        }
    },
    {
        'name': "microsoft",
        'issuer': 'https://login.microsoftonline.com/consumers/v2.0',
        'allowed_email_domains': ['hotmail.com', 'live.com', 'outlook.com'],
        'credential': {
            'kind': 'ClientSecret',
            'client_id': os.environ['WEBID_MICROSOFT_CLIENT_ID'],
            'client_secret': os.environ['WEBID_MICROSOFT_CLIENT_SECRET']
        }
    },
    {
        'name': "yahoo",
        'issuer': 'https://api.login.yahoo.com',
        'allowed_email_domains': ['yahoo.com'],
        'credential': {
            'kind': 'ClientSecret',
            'client_id': os.environ['WEBID_YAHOO_CLIENT_ID'],
            'client_secret': os.environ['WEBID_YAHOO_CLIENT_SECRET']
        }
    },
]


app: Service = Service()
app.add(
    oauth2.AuthorizationServer(
        client=True,
        #downstream={
        #    'protocol': 'oidc',
        #    'allowed_email_domains': [
        #        'buymolano.com',
        #        'molano.nl',
        #        'refurbcity.nl'
        #    ],
        #    'name': 'molano',
        #    'contacts': [
        #        'Noek de Feber <n.defeber@molano.nl>',
        #        'Cochise Ruhulessin <c.ruhulessin@.molano.nl>',
        #    ],
        #    'credential': {
        #        'kind': 'ClientSecret',
        #        'client_id': os.environ['MOLANO_WEBIAM_CLIENT_ID'],
        #        'client_secret': os.environ['MOLANO_WEBIAM_CLIENT_SECRET'],
        #    },
        #    'issuer': 'https://accounts.google.com',
        #    'scope': {'email', 'openid', 'profile'},
        #    'params': {'hd': 'molano.nl'}
        #},
        response_types=[
            oauth2.types.ResponseType.code
        ]
    ),
    prefix='/oauth2'
)


@app.on_event('startup')
def f():
    print('https://localhost.webiam.id/oauth2/authorize?client_id=self&response_type=code&state=foo')


if __name__ == '__main__':
    uvicorn.run('__main__:app', reload=True, port=6004) # type: ignore