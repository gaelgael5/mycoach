"""Interface SMS + providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SmsResult:
    success: bool
    provider_message_id: str | None = None
    error_message: str | None = None


class SmsProvider(ABC):
    @abstractmethod
    async def send(self, to: str, body: str) -> SmsResult: ...


class ConsoleSmsProvider(SmsProvider):
    """Dev/test — log uniquement, pas d'envoi réel."""

    async def send(self, to: str, body: str) -> SmsResult:
        import logging
        logging.getLogger(__name__).info(f"[SMS CONSOLE] to={to} body={body[:50]}...")
        return SmsResult(success=True, provider_message_id="console_mock_id")


class TwilioSmsProvider(SmsProvider):
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    async def send(self, to: str, body: str) -> SmsResult:
        try:
            import asyncio
            from twilio.rest import Client as TwilioClient
            loop = asyncio.get_event_loop()
            client = TwilioClient(self.account_sid, self.auth_token)
            msg = await loop.run_in_executor(
                None,
                lambda: client.messages.create(body=body, from_=self.from_number, to=to)
            )
            return SmsResult(success=True, provider_message_id=msg.sid)
        except Exception as e:
            return SmsResult(success=False, error_message=str(e))


def get_sms_provider() -> SmsProvider:
    """Factory : retourne ConsoleSmsProvider en dev/test, Twilio en prod."""
    from app.config import get_settings
    settings = get_settings()
    if getattr(settings, 'APP_ENV', 'development') == 'production':
        return TwilioSmsProvider(
            account_sid=getattr(settings, 'TWILIO_ACCOUNT_SID', ''),
            auth_token=getattr(settings, 'TWILIO_AUTH_TOKEN', ''),
            from_number=getattr(settings, 'TWILIO_FROM_NUMBER', ''),
        )
    return ConsoleSmsProvider()
