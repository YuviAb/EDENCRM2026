"""
הגדרות גלובליות לאפליקציה.
כל הערכים נטענים מקובץ .env (ראה .env.example).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    APP_NAME: str = "Facial Clinic CRM"
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "http://localhost:5173"

    # Supabase
    SUPABASE_URL: str
    SUPABASE_ANON_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_STORAGE_BUCKET: str = "client-photos"

    # Google Calendar (אופציונלי — ריק = סנכרון כבוי)
    GOOGLE_SERVICE_ACCOUNT_FILE: str = ""
    GOOGLE_CALENDAR_ID: str = ""

    # WhatsApp / Twilio (אופציונלי — ריק = שליחה מושבתת)
    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: str = ""
    TWILIO_WHATSAPP_FROM: str = "whatsapp:+14155238886"
    CLINIC_OWNER_WHATSAPP_NUMBER: str = ""
    DAILY_REMINDER_HOUR: int = 6

    # Intake
    INTAKE_SECRET: str = ""

    # Auth / JWT
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""  # צור עם: python generate_password.py
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 8

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
