from abc import ABC, abstractmethod


class WhatsAppSender(ABC):
    """
    ממשק שליחת WhatsApp.
    כל מימוש (Twilio, Meta Cloud API, וכו') מרחיב מחלקה זו.
    """

    @abstractmethod
    def send_message(self, to: str, body: str) -> bool:
        """
        שולח הודעת WhatsApp.

        to   — מספר יעד בפורמט 'whatsapp:+972XXXXXXXXX'
        body — גוף ההודעה
        מחזיר True בהצלחה, False בכישלון.
        """
