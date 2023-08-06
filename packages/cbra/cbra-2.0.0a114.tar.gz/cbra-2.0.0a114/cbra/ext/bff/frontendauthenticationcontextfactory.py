# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import logging

import cbra.core as cbra
from cbra.types import IDependant
from cbra.types import ISubjectResolver
from cbra.core.iam import AuthenticationService
from cbra.core.iam import AuthorizationContextFactory
from .frontendsubjectresolver import FrontendSubjectResolver
from .oidcrequestsubject import OIDCRequestSubject


class FrontendAuthorizationContextFactory(AuthorizationContextFactory, IDependant):
    """The default implementation of :class:`~cbra.types.IAuthorizationContextFactory`"""
    __module__: str = 'cbra.core.iam'
    authentication: AuthenticationService
    logger: logging.Logger = logging.getLogger('uvicorn')
    resolver: ISubjectResolver
    subject: OIDCRequestSubject

    def __init__(
        self,
        resolver: FrontendSubjectResolver = FrontendSubjectResolver.depends(),
        authentication: AuthenticationService = cbra.instance(
            name='AuthenticationService',
            missing=AuthenticationService
        )
    ):
        self.authentication = authentication
        self.resolver = resolver