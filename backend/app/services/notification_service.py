"""Service notifications push — B2-16."""
import logging
from app.utils.i18n import t

logger = logging.getLogger(__name__)


class NotificationService:
    async def send_push(self, user_id, title_key: str, body_key: str, data: dict, locale: str = "fr") -> bool:
        """Stub Firebase — à remplacer avec firebase_admin en Phase 6."""
        title = t(title_key, locale)
        body = t(body_key, locale)
        logger.info(f"[PUSH STUB] user={user_id} title={title!r} body={body!r} data={data}")
        return True


notification_service = NotificationService()
