from app.features.contact.schemas import ContactFormIn
from app.features.notifications.service import NotificationService


class ContactService:

    def __init__(self) -> None:
        self._notif = NotificationService()

    async def submit(self, payload: ContactFormIn) -> None:
        await self._notif.alert_admin_contact(payload.name, payload.email, payload.message)
        await self._notif.send_contact_auto_reply(payload.email, payload.name)
