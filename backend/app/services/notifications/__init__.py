"""
Factory לשליחת WhatsApp.
כל קוד שרוצה לשלוח הודעה קורא ל-get_whatsapp_sender() בלבד —
אין תלות ישירה ב-Twilio מחוץ לקובץ twilio_sender.py.
כדי לעבור לספק אחר (Meta Cloud API וכו'): החלף מחלקה כאן ורק כאן.
"""
from app.services.notifications.base import WhatsAppSender
from app.services.notifications.twilio_sender import TwilioWhatsAppSender

_sender: WhatsAppSender | None = None


def get_whatsapp_sender() -> WhatsAppSender:
    global _sender
    if _sender is None:
        _sender = TwilioWhatsAppSender()
    return _sender
