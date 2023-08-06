# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
from typing import cast
from typing import Any

from canonical import EmailAddress

import cbra.core as cbra
from cbra.core.conf import settings
from cbra.types import IPolymorphicRepository
from cbra.types import PersistedModel
from cbra.types import Ratelimited
from cbra.types import IEmailSender
from ..models import EmailChallenge
from ..types import IEmailChallenge
from .models import EmailChallengeRequest
from .models import EmailChallengeResponse
from .models import EmailChallengeSolutionRequest
from .models import EmailChallengeSolutionResponse


class EmailChallengeEndpoint(cbra.Endpoint):
    email_template: str = 'email-verification.html.j2'
    email: IEmailSender = cbra.instance('EmailSender')
    model: type[IEmailChallenge] = EmailChallenge
    require_authentication: bool = False
    response_model_by_alias: bool = True

    def get_email_sender(self) -> str:
        assert settings.EMAIL_DEFAULT_SENDER is not None
        return settings.EMAIL_DEFAULT_SENDER

    async def post(
        self,
        dto: EmailChallengeSolutionRequest | EmailChallengeRequest,
        repo: IPolymorphicRepository = cbra.instance('PolymorphicRepository')
    ) -> EmailChallengeResponse | EmailChallengeSolutionResponse:
        """Provides an interface to create and solve a challenge to
        verify the ownership of an email address.

        To create a challenge, issue a `POST` request containing a JSON
        object of type `EmailChallengeRequest` as the request body. The
        response contains a JSON object of type `EmailChallengeResponse`.
        The client must retain the included `challengeId`. An email is
        sent to the email address (provided with the `email` parameter
        in the request body) containing a verification code.
        """
        handler = self.handle_create if dto.is_request() else self.handle_solve
        return await handler(dto, repo) # type: ignore

    async def handle_create(
        self,
        dto: EmailChallengeRequest,
        repo: IPolymorphicRepository
    ) -> EmailChallengeResponse:
        # Check if an existing challenge exists for this emailaddress,
        # and if it is not old enough, refuse to create a new challenge.
        challenge = await self.retrieve_challenge_by_email(repo, dto.email)
        if challenge and challenge.age() < 60:
            raise Ratelimited
        challenge = await self.create_challenge(dto)
        await self.persist_challenge(repo, challenge)
        await self.on_challenge_created(challenge)
        return EmailChallengeResponse(
            challengeId=challenge.get_challenge_id()
        )

    async def handle_solve(
        self,
        dto: EmailChallengeSolutionRequest,
        repo: IPolymorphicRepository
    ) -> EmailChallengeSolutionResponse:
        challenge = await self.retrieve_challenge(repo, dto.challenge_id)
        if not challenge or challenge.is_blocked():
            return EmailChallengeSolutionResponse(
                success=False,
                blocked=True
            )
        is_solved = challenge.verify(dto.code)
        if is_solved:
            await self.on_challenge_solved(challenge, dto)
        await self.persist_challenge(repo, challenge)
        return EmailChallengeSolutionResponse(
            success=is_solved,
            blocked=challenge.is_blocked()
        )

    async def create_challenge(self, dto: Any) -> IEmailChallenge:
        return self.model.new(dto.email)

    async def retrieve_challenge(
        self,
        repo: IPolymorphicRepository,
        challenge_id: str
    ) -> IEmailChallenge:
        return await repo.get(self.model, challenge_id) # type: ignore
    
    async def retrieve_challenge_by_email(
        self,
        repo: IPolymorphicRepository,
        email: str
    ) -> IEmailChallenge | None:
        return await repo.find(self.model, [('email', '=', email)], ['-requested']) # type: ignore

    async def persist_challenge(
        self,
        repo: IPolymorphicRepository,
        challenge: IEmailChallenge
    ) -> None:
        await repo.persist(cast(PersistedModel, challenge))

    async def on_challenge_created(self, challenge: IEmailChallenge) -> None:
        pass

    async def on_challenge_requested(self, email: EmailAddress) -> None:
        raise NotImplementedError
    
    async def on_challenge_solved(self, challenge: Any, dto: Any) -> None:
        raise NotImplementedError