# Copyright (C) 2023 Cochise Ruhulessin
#
# All rights reserved. No warranty, explicit or implicit, provided. In
# no event shall the author(s) be liable for any claim or damages.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import asyncio
import logging
import os
from types import EllipsisType
from typing import cast
from typing import Any

import sendgrid
from sendgrid.helpers.mail import Attachment
from sendgrid.helpers.mail import Content
from sendgrid.helpers.mail import ContentId
from sendgrid.helpers.mail import Disposition
from sendgrid.helpers.mail import Email
from sendgrid.helpers.mail import FileContent
from sendgrid.helpers.mail import FileName
from sendgrid.helpers.mail import FileType
from sendgrid.helpers.mail import Mail
from sendgrid.helpers.mail import Subject
from sendgrid.helpers.mail import To

from cbra.core.conf import settings
from cbra.types import ServiceNotAvailable
from cbra.ext.email import BaseEmailSender


class SendgridEmailSender(BaseEmailSender):
    __module__: str = 'cbra.ext.sendgrid'
    logger: logging.Logger = logging.getLogger('cbra.endpoint')

    @property
    def sendgrid_api_key(self) -> str:
        if not os.getenv('SENDGRID_API_KEY'):
            self.logger.critical("SENDGRID_API_KEY not specified in environment")
            raise ServiceNotAvailable
        return cast(str, os.getenv('SENDGRID_API_KEY'))

    @property
    def client(self) -> sendgrid.SendGridAPIClient:
        c =  sendgrid.SendGridAPIClient(
            api_key=self.sendgrid_api_key)
        c.client.timeout = 10 # type: ignore
        return c

    async def send_template(
        self,
        sender: str | EllipsisType,
        recipients: list[str],
        subject: str,
        template: str | None = None,
        templates: dict[str, str] | None = None,
        context: dict[str, Any] | None = None,
        content_type: str = "text/html",
        headers: dict[str, Any] | None = None,
        cc: list[str] | None = None,
        bcc: list[str] | None = None,
        attachments: list[dict[str, Any]] | None = None
    ) -> None:
        """Render a template and send it as email to the specified
        recipients.
        """
        if not bool(template) ^ bool(templates):
            raise TypeError("Provide the template or templates parameter.")
        if template:
            templates = {content_type: template}

        assert isinstance(templates, dict)
        ctx: dict[str, Any] = context or {}
        if sender == ...:
            if settings.EMAIL_DEFAULT_SENDER is None:
                raise TypeError('Declare EMAIL_DEFAULT_SENDER in settings')
            sender = settings.EMAIL_DEFAULT_SENDER
        msg = Mail()
        msg.to = [To(x) for x in recipients]
        msg.from_email = Email(sender)
        msg.subject = Subject(subject)
        content: list[Content] = []
        for content_type, body in self.render_templates(templates, ctx):
            content.append(Content(content_type, body))
        msg.content = content
        for params in (attachments or []):
            attachment = Attachment()
            attachment.content_id = ContentId(params['content_id'])
            attachment.file_type = FileType(params['content_type'])
            attachment.file_content = FileContent(params['content'])
            attachment.file_name = FileName(params['filename'])
            attachment.disposition = Disposition('attachment')
            msg.add_attachment(attachment)

        await self._send(msg)

    async def _send(self, msg: Mail) -> bool:
        loop = asyncio.get_running_loop()
        f = self.client.send # type: ignore
        from python_http_client.exceptions import HTTPError

        try:
            response = await loop.run_in_executor( # type: ignore
                None, lambda: f(msg)) # type: ignore
        except HTTPError as e:
            raise Exception(e.to_dict)
        except Exception as e: # pylint: disable=broad-except
            if not hasattr(e, 'status_code'):
                raise
            response = e
            self.logger.critical(
                "Failed to send email (response: %s)",
                response.status_code # type: ignore
            )
            raise ServiceNotAvailable
        if response.status_code >= 400: # type: ignore
            self.logger.critical(
                "Failed to send email (response: %s)",
                response.status_code # type: ignore
            )
            raise ServiceNotAvailable

        return True