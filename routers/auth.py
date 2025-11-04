from fastapi import APIRouter, HTTPException, Request, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .crud import read_records, create_record
import os
import httpx
from datetime import datetime, timedelta
from dotenv import load_dotenv
from jose import jwt
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_AUTH_URL = f"{SUPABASE_URL}/auth/v1"
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_SSL_TLS=False,  # Changed from MAIL_SSL
    MAIL_STARTTLS=True,  # Changed from MAIL_TLS
    USE_CREDENTIALS=True
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

security = HTTPBearer()

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

@router.post("/register")
async def register(payload: dict):
    """
    Register new user as landlord or house seeker.
    Payload: { "email": "...", "password": "...", "role": "landlord" | "user" }
    """
    email = payload.get("email")
    password = payload.get("password")
    role = payload.get("role", "user")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required.")
    if role not in ["landlord", "user"]:
        raise HTTPException(status_code=400, detail="Role must be 'landlord' or 'user'.")
    # Register in Supabase Auth
    url = f"{SUPABASE_AUTH_URL}/signup"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=get_supabase_headers(), json={"email": email, "password": password})
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        user_info = resp.json()
        user_id = user_info.get("user", {}).get("id")
        # Register in users table with helper
        if user_id:
            try:
                await create_record("users", {
                    "id": user_id,
                    "email": email,
                    "role": role
                })
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    return {"msg": "Registration successful.", "user": user_info}

@router.post("/login")
async def login(payload: dict):
    """
    Login with email + password (returns JWT access token).
    Payload: { "email": "...", "password": "..." }
    """
    email = payload.get("email")
    password = payload.get("password")
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required.")

    url = f"{SUPABASE_AUTH_URL}/token?grant_type=password"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=get_supabase_headers(), json={"email": email, "password": password})
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        data = resp.json()
    return {"msg": "Login successful.", "auth": data}

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifies Supabase JWT for protected routes.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    return payload

@router.get("/me")
async def get_user_me(user=Depends(verify_jwt_token)):
    """
    Returns authenticated user's info and role.
    """
    user_id = user.get("sub")
    try:
        profile = await read_records("users", f"id=eq.{user_id}", "email,role")
        return {"user": user, "profile": profile[0] if profile else None}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Could not retrieve user info")

# LANDLORD LISTING LICENSE CHECK (helper for listings.py etc)
async def check_landlord_can_list(user_id):
    now = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    try:
        payments = await read_records(
            "payments",
            f"user_id=eq.{user_id}&confirmed=eq.true&created_at=gte.{month_start.isoformat()}",
        )
        if not payments:
            raise HTTPException(
                status_code=402,
                detail="Renew your monthly landlord license/payment to list houses."
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# === AUTOMATED EMAIL REMINDER ===
async def get_landlords_needing_payment_reminder():
    try:
        landlords = await read_records("users", "role=eq.landlord", "id,email")
        reminder_list = []
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month_start = (month_start + timedelta(days=32)).replace(day=1)
        for landlord in landlords:
            user_id = landlord["id"]
            payments = await read_records(
                "payments",
                f"user_id=eq.{user_id}&confirmed=eq.true&created_at=gte.{month_start.isoformat()}&created_at=lt.{next_month_start.isoformat()}"
            )
            if not payments and now.day > 23:  # Remind during last week
                reminder_list.append(landlord["email"])
        return reminder_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def send_reminder_email(recipient_email, fm: FastMail):
    subject = "Renew your KejaHunt monthly listing license"
    body = (
        "Dear Landlord,\n\n"
        "Your monthly listing license is about to expire. Please pay your listing fee to continue posting properties on KejaHunt. If you've already paid, you can ignore this message!\n\n"
        "Thank you for using KejaHunt."
    )
    message = MessageSchema(
        subject=subject,
        recipients=[recipient_email],
        body=body,
        subtype="plain"
    )
    await fm.send_message(message)

@router.post("/send_landlord_payment_reminders")
async def run_landlord_reminder_emails(background_tasks: BackgroundTasks):
    """
    Call this endpoint (manually, with a scheduler, or a CRON job) to send payment reminders.
    """
    emails = await get_landlords_needing_payment_reminder()
    fm = FastMail(conf)
    for email in emails:
        background_tasks.add_task(send_reminder_email, email, fm)
    return {"success": True, "emails_sent": emails}
