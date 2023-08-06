# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import enum


class PromptType(str, enum.Enum):
    #: The Authorization Server must not display any authentication or
    #: consent user interface pages. An error is returned if an
    #: End-User is not already authenticated or the Client does not
    #: have pre-configured consent for the requested Claims or does
    #: not fulfill other conditions for processing the request.
    #: The error code will typically be ``login_required``,
    #: ``interaction_required``, or another code defined the OpenID
    #: Connect standard. This can be used as a method to check for
    #: existing authentication and/or consent.
    none = 'none'

    #: The Authorization Server should prompt the End-User for
    #: reauthentication. If it cannot reauthenticate the End-User,
    #: it must return an error, typically ``login_required``.
    login = 'login'

    #: The Authorization Server should prompt the End-User for
    #: consent before returning information to the Client.
    #: If it cannot obtain consent, it must return an error,
    #: typically ``consent_required``.
    consent = 'consent'

    #: The Authorization Server should prompt the End-User to select a user
    #: account. This enables an End-User who has multiple accounts at
    #: the Authorization Server to select amongst the multiple accounts
    #: that they might have current sessions for. If it cannot obtain
    #: an account selection choice made by the End-User, it must return
    #: an error, typically ``account_selection_required``.
    select_account = 'select_account'