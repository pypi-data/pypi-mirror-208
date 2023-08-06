# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime

import pydantic


class PicklistShipment(pydantic.BaseModel):
    idshipment: int
    idpicklist: int
    idorder: int
    idreturn: int | None = None
    idshippingprovider: int
    idcompany_shippingprovider: int
    idcompany_shippingprovider_profile: int
    provider: str
    providername: str
    public_providername: str
    profile_name: str
    carrier_key: str
    labelurl_pdf: str | None = None
    labelurl_zpl: str | None = None
    trackingcode: str | None = None
    trackingurl: str | None = None
    tracktraceurl: str | None = None
    created_by_iduser: int
    cancelled: bool = False
    created: datetime.datetime
    updated: datetime.datetime