# Facial Clinic CRM — Backend

שרת FastAPI לניהול לקוחות, יומן תורים, תשלומים ותמונות עבור קליניקת טיפולי פנים.

## מבנה הפרויקט

```
backend/
├── app/
│   ├── main.py              # נקודת הכניסה - FastAPI app
│   ├── core/
│   │   ├── config.py        # הגדרות וטעינת .env
│   │   └── supabase_client.py
│   ├── schemas/             # מודלי Pydantic (validation)
│   │   ├── client.py
│   │   ├── appointment.py
│   │   ├── payment.py
│   │   └── photo.py
│   ├── services/            # לוגיקה עסקית + תקשורת עם Supabase
│   │   ├── client_service.py
│   │   ├── appointment_service.py
│   │   ├── payment_service.py
│   │   └── photo_service.py
│   └── api/                 # נקודות הקצה (routes)
│       ├── clients.py
│       ├── appointments.py
│       ├── payments.py
│       └── photos.py
├── supabase_schema.sql      # סכמת DB - להרצה ב-Supabase SQL Editor
├── requirements.txt
└── .env.example
```

## הרצה מקומית

1. **צור סביבה וירטואלית והתקן תלויות:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate    # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **הגדר משתני סביבה:**
   ```bash
   cp .env.example .env
   ```
   ואז מלא ב-`.env` את הערכים מ-Supabase (URL + מפתחות) — נעבור על זה בשלב הבא.

3. **הרץ את השרת:**
   ```bash
   uvicorn app.main:app --reload
   ```

4. **בדוק שזה עובד:**
   - `http://localhost:8000` — health check
   - `http://localhost:8000/docs` — תיעוד אוטומטי (Swagger UI) עם כל ה-endpoints, אפשר לבדוק שם הכל ישירות מהדפדפן

## מצב נוכחי (שלב 1)

✅ מבנה פרויקט מלא
✅ 4 ישויות: לקוחות, תורים, תשלומים, תמונות
✅ CRUD מלא לכל ישות
✅ העלאת תמונות ל-Supabase Storage
✅ סכמת SQL מוכנה להרצה

## עדיין לא בשלב הזה (יגיע בהמשך)

- Authentication (התחברות עם סיסמה)
- Frontend בפועל (יש לנו רק תיקייה ריקה)
- אוטומציות תזכורות (אימייל/וואטסאפ)
- Deploy לענן
