from app.services.notifications.base import WhatsAppSender
from app.core.config import settings


class TwilioWhatsAppSender(WhatsAppSender):
    """
    שליחת WhatsApp דרך Twilio Sandbox.
    אם פרטי ההתחברות חסרים — השירות מושבת בשקט (לא קורס את השרת).
    """

    def __init__(self):
        self._client = None
        configured = all([
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.CLINIC_OWNER_WHATSAPP_NUMBER,
        ])
        if configured:
            try:
                from twilio.rest import Client
                self._client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                print("[WhatsApp] Twilio ready")
            except Exception as exc:
                print(f"[WhatsApp] שגיאה באתחול Twilio: {exc}")

    @property
    def enabled(self) -> bool:
        return self._client is not None

    def send_message(self, to: str, body: str) -> bool:
        if not self.enabled:
            print("[WhatsApp] שליחה מושבתת — הגדר TWILIO_* ב-.env")
            return False
        try:
            msg = self._client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=to,
                body=body,
            )
            print(f"[WhatsApp] sent OK - SID={msg.sid}")
            return True
        except Exception as exc:
            print(f"[WhatsApp] שגיאת שליחה: {exc}")
            return False
