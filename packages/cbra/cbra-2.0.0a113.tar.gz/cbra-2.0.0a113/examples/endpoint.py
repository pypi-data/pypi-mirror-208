# Copyright (C) 2021-2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import uuid

import fastapi
import uvicorn

import cbra


class BookEndpoint(cbra.Endpoint):

    async def get(self, book_id: uuid.UUID):
        print(self.response)


app = fastapi.FastAPI(docs_url='/ui')
BookEndpoint.add_to_router(app, path='/books/{book_id}')


if __name__ == '__main__':
    uvicorn.run('__main__:app', reload=True) # type: ignore
