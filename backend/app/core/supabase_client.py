"""
חיבור יחיד (singleton) ל-Supabase, משמש בכל שירותי האפליקציה.

שני קליינטים:
- supabase_admin: משתמש ב-Service Role Key, עוקף RLS. שימוש בקוד השרת בלבד.
- supabase_anon:  משתמש ב-Anon Key, מכבד RLS. שמור לעתיד אם נחשוף קריאות מהפרונט ישירות.
"""
from functools import lru_cache
from supabase import create_client, Client
from app.core.config import settings


@lru_cache
def get_supabase_admin() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@lru_cache
def get_supabase_anon() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
