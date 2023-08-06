# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import datetime
from typing import Literal

import pydantic
from canonical import ISO3166Alpha2
from canonical import TimezoneInfo


class SelfAssertedClaims(pydantic.BaseModel):
    cor: ISO3166Alpha2 | None = pydantic.Field(
        default=None,
        title="Country of Residence",
        max_length=2,
        description="The country an End-User is currently residing in."
    )

    initials: str | None = pydantic.Field(
        default=None,
        title="Initials",
        max_length=16,
        description="The initials of the End-User."
    )

    given_name: str | None = pydantic.Field(
        default=None,
        title="Given name",
        max_length=64,
        description=(
            "Given name(s) or first name(s) of the End-User. Note that in some "
            "cultures, people can have multiple given names; all can be present, "
            "with the names being separated by space characters."
        )
    )

    family_name: str | None = pydantic.Field(
        default=None,
        title="Family name",
        max_length=64,
        description=(
            "Surname(s) or last name(s) of the End-User. Note that in some cultures, "
            "people can have multiple family names or no family name; all can be "
            "present, with the names being separated by space characters."
        )
    )

    name_order: Literal['western', 'eastern'] | None = pydantic.Field(
        default=None,
        title="Name order",
        description="The order in which the name of the End-User is written."
    )

    middle_name: str | None = pydantic.Field(
        default=None,
        title="Middle name",
        max_length=64,
        description=(
            "Middle name(s) of the End-User. Note that in some cultures, people can "
            "have multiple middle names; all can be present, with the names being "
            "separated by space characters. Also note that in some cultures, middle "
            "names are not used."
        )
    )

    nickname: str | None = pydantic.Field(
        default=None,
        title="Nickname",
        max_length=64,
        description=(
            "Casual name of the End-User that may or may not be the same as "
            "the `given_name`. For instance, a `nickname` value of `Mike` "
            "might be returned alongside a `given_name` value of `Michael`."
        )
    )

    gender: Literal['male', 'female', 'other'] | None = pydantic.Field(
        default=None,
        title="Gender",
        description=(
            "End-User's gender. Values defined by this specification are "
            "`female` and `male`. Other values MAY be used when neither "
            "of the defined values are applicable."
        )
    )

    birthdate: datetime.date | str | None = pydantic.Field(
        default=None,
        title="Birthdate",
        max_length=8,
        description=(
            "End-User's birthday, represented as an ISO 8601:2004 `YYYY-MM-DD` "
            "format. The year MAY be `0000`, indicating that it is omitted. "
            "To represent only the year, `YYYY` format is allowed. Note that "
            "depending on the underlying platform's date related function, "
            "providing just year can result in varying month and day, so the "
            "implementers need to take this factor into account to correctly "
            "process the dates."
        )
    )

    zoneinfo: TimezoneInfo | None = pydantic.Field(
        default=None,
        title="Timezone",
        max_length=64,
        description=(
            "String from zoneinfo time zone database representing the "
            "End-User's time zone. For example, `Europe/Paris` or "
            "`America/Los_Angeles`."
        )
    )

    locale: str | None = pydantic.Field(
        default=None,
        title="Locale",
        max_length=32,
        description=(
            "End-User's locale, represented as a BCP47 language tag. This is "
            "typically an ISO 639-1 Alpha-2 language code in lowercase and "
            "an ISO 3166-1 Alpha-2 country code in uppercase, separated by "
            "a dash. For example, `en-US` or `fr-CA`. As a compatibility "
            "note, some implementations have used an underscore as the "
            "separator rather than a dash, for example, `en_US`; "
            "Relying Parties MAY choose to accept this locale syntax as well."
        )
    )