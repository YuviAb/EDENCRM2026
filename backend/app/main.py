"""
נקודת הכניסה הראשית של אפליקציית ה-FastAPI.
הרצה: uvicorn app.main:app --reload
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError as PostgrestAPIError

from app.core.config import settings
from app.core.deps import require_admin
from app.api import clients, appointments, payments, photos, dashboard, notifications, auth, intake


# ── Scheduler (APScheduler) ──────────────────────────────────────────
def _start_scheduler():
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from app.services.daily_reminder_service import send_daily_reminder

        scheduler = BackgroundScheduler(timezone="Asia/Jerusalem")
        scheduler.add_job(
            send_daily_reminder,
            CronTrigger(hour=settings.DAILY_REMINDER_HOUR, minute=0, timezone="Asia/Jerusalem"),
            id="daily_whatsapp_reminder",
            replace_existing=True,
        )
        scheduler.start()
        print(f"[Scheduler] Daily reminder scheduled at {settings.DAILY_REMINDER_HOUR}:00 (Asia/Jerusalem)")
        return scheduler
    except Exception as exc:
        print(f"[Scheduler] Failed to start: {exc}")
        return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = _start_scheduler()
    yield
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)


# ── App ──────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description="מערכת ניהול לקוחות למרפאת טיפולי פנים.",
    version="0.1.0",
    lifespan=lifespan,
    # הסתרת /docs ו-/openapi.json בפרודקשן
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Security headers middleware ───────────────────────────────────────
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"]  = "nosniff"
    response.headers["X-Frame-Options"]          = "DENY"
    response.headers["X-XSS-Protection"]         = "1; mode=block"
    response.headers["Referrer-Policy"]           = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"]        = "camera=(), microphone=(), geolocation=()"
    # מסתיר את שם ה-server framework
    response.headers["Server"]                    = "eden"
    return response


# ── Exception Handlers ───────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "שגיאת ולידציה בבקשה", "detail": exc.errors()},
    )


@app.exception_handler(PostgrestAPIError)
async def postgrest_error_handler(request: Request, exc: PostgrestAPIError):
    return JSONResponse(
        status_code=500,
        content={"error": "שגיאת מסד נתונים", "detail": str(exc)},
    )


# ── Auth router (public — no token required) ─────────────────────────
app.include_router(auth.router, prefix="/api")

# ── Protected routers (require valid JWT) ────────────────────────────
_auth = [Depends(require_admin)]

app.include_router(clients.router,       prefix="/api", dependencies=_auth)
app.include_router(appointments.router,  prefix="/api", dependencies=_auth)
app.include_router(payments.router,      prefix="/api", dependencies=_auth)
app.include_router(photos.router,        prefix="/api", dependencies=_auth)
app.include_router(dashboard.router,     prefix="/api", dependencies=_auth)
app.include_router(notifications.router, prefix="/api", dependencies=_auth)

# ── Intake router (public — no token required) ────────────────────────
app.include_router(intake.router, prefix="/api")


# ── Root endpoints ────────────────────────────────────────────────────
@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
