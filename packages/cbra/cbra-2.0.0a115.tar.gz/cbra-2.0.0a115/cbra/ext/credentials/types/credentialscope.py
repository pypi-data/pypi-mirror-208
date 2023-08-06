# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import enum


class CredentialScope(str, enum.Enum):
    #: Global, application-level scope. Use this type for credentials that
    #: can not be provided through configuration (such as environment
    #: variables), for example credentials obtained from an authorization
    #: server.
    GLOBAL = 'GLOBAL'

    #: The credentials are scoped to a single account, or similar (
    #: such as a Subscription in Microsoft Azure or an Organization on
    #: Google Cloud Platform).
    ACCOUNT = 'ACCOUNT'

    #: The credentials are scoped to a single subject.
    SUBJECT = 'SUBJECT'