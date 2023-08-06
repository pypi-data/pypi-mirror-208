# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import fastapi
from headless.ext.picqer import DefaultClient

from cbra.ext import google
from cbra.ext import picqer



class PicqerWebhookEndpoint(picqer.PicqerWebhookEndpoint):

    async def on_picklists_created(self, event: picqer.v1.PicklistEvent):
        return fastapi.Response(content=event.json(indent=2))


app = google.Service(docs_url='/ui')
app.add(PicqerWebhookEndpoint, path='/ext/picqer.com/v1/.webhooks')


@app.post('/ext/picqer.com/v1/.webhooks/install')
async def f(request: fastapi.Request):
    async with DefaultClient() as client:
        await PicqerWebhookEndpoint.install(
            client,
            callback_url=request.url_for('picqer.webhooks'),
            generate_name=lambda x: (
                f"{str.join('.', reversed(str.split(x, '.')))}"
                f".picqer.{request.url.netloc}"
            ),
            secret='test'
        )


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('__main__:app', reload=True) # type: ignore
