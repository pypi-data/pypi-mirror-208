# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import os

os.environ['PYTHON_SETTINGS_MODULE'] = __name__

OAUTH2_CLIENTS = [
    {
        'name': 'google',
        'issuer': 'https://accounts.google.com',
        'client_id': '641438517445-22t22tlpnbk4a7575a89js6csko51e6a.apps.googleusercontent.com',
        'client_secret': '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',
        'trust_email': True,
        'scope': {'email', 'profile'}
    }
]

SECRET_KEY: str = 'changeme'

from typing import Any

import cbra.core as cbra
from cbra.ext import google
from cbra.ext.oauth2 import OIDCRegistrationEndpoint
from cbra.ext.oauth2 import LoginEndpoint


class HomeEndpoint(cbra.Endpoint):

    async def get(self) -> dict[str, Any]:
        await self.session
        return {
            'claims': self.session.claims.dict()
        }


app = google.Service(docs_url='/ui')
app.add(OIDCRegistrationEndpoint, path='/oauth2/callback/{client_id}')
app.add(LoginEndpoint, path='/oauth2/login/{client_id}')
app.add(HomeEndpoint, path='/')

OAUTH2_STATE: str = os.urandom(32).hex()


@app.on_event('startup')
async def boot():
    url = "http://localhost:8000/oauth2/login/google"
    print(f"Open {url} to initiate the flow.")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('__main__:app', reload=True) # type: ignore
