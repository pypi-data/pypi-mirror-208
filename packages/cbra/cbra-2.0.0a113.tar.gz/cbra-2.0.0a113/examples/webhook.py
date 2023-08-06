# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import uvicorn
import cbra.core as cbra


URL = "https://eop5zsb1qet1zjc.m.pipedream.net"

DEFAULT_API_VERSION: str = '2023-01'

from cbra.ext.shopify import ShopifyWebhookEndpoint


app: cbra.Application = cbra.Application()
app.add(ShopifyWebhookEndpoint)
if __name__ == '__main__':
    uvicorn.run('__main__:app', reload=True) # type: ignore