import json
from urllib import error, request

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class AppsScriptEmailBackend(BaseEmailBackend):
    """
    Send Django email through the private Google Apps Script gateway.
    """

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        gateway_url = settings.BLOGGIFY_MAIL_GATEWAY_URL
        gateway_token = settings.BLOGGIFY_MAIL_GATEWAY_TOKEN

        if not gateway_url or not gateway_token:
            if self.fail_silently:
                return 0

            raise RuntimeError(
                "BLOGGIFY_MAIL_GATEWAY_URL and "
                "BLOGGIFY_MAIL_GATEWAY_TOKEN are required."
            )

        sent_count = 0

        for message in email_messages:
            recipients = message.recipients()

            if not recipients:
                continue

            try:
                html_body = self._get_html_body(message)

                for recipient in recipients:
                    self._send_one(
                        gateway_url=gateway_url,
                        gateway_token=gateway_token,
                        recipient=recipient,
                        subject=message.subject or "",
                        text_body=message.body or "",
                        html_body=html_body,
                    )

                sent_count += 1

            except Exception:
                if not self.fail_silently:
                    raise

        return sent_count

    @staticmethod
    def _send_one(
        gateway_url,
        gateway_token,
        recipient,
        subject,
        text_body,
        html_body,
    ):
        payload = json.dumps(
            {
                "token": gateway_token,
                "to": recipient,
                "subject": subject,
                "text": text_body,
                "html": html_body,
            }
        ).encode("utf-8")

        gateway_request = request.Request(
            gateway_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Bloggify/1.0",
            },
            method="POST",
        )

        try:
            with request.urlopen(
                gateway_request,
                timeout=getattr(settings, "EMAIL_TIMEOUT", 15),
            ) as response:
                raw_response = response.read().decode("utf-8")
                result = json.loads(raw_response)

        except (error.HTTPError, error.URLError, TimeoutError) as exc:
            raise RuntimeError(
                f"Apps Script mail gateway request failed: {exc}"
            ) from exc

        if not result.get("ok"):
            raise RuntimeError(
                f"Apps Script mail gateway rejected the email: {result}"
            )

    @staticmethod
    def _get_html_body(message):
        for alternative in getattr(message, "alternatives", ()):
            content = getattr(alternative, "content", None)
            mimetype = getattr(alternative, "mimetype", None)

            if content is None and isinstance(alternative, (tuple, list)):
                content, mimetype = alternative

            if mimetype == "text/html":
                return content

        return ""
