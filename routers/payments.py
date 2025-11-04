from fastapi import APIRouter, HTTPException, Query, Request
from .crud import read_records, create_record, update_record
import os
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

PAYMENTS_TABLE = "payments"
USERS_TABLE = "users"
LISTINGS_TABLE = "listings"

router = APIRouter(
    prefix="/payments",
    tags=["payments"]
)

# Helper: Validate foreign key existence using crud helpers
async def validate_user_and_listing(user_id: int, listing_id: int) -> None:
    try:
        user = await read_records(USERS_TABLE, f"id=eq.{user_id}", "id")
        if not user:
            raise HTTPException(status_code=400, detail="Invalid user_id")
        listing = await read_records(LISTINGS_TABLE, f"id=eq.{listing_id}", "id")
        if not listing:
            raise HTTPException(status_code=400, detail="Invalid listing_id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_payments(user_id: Optional[int] = Query(None), listing_id: Optional[int] = Query(None)):
    """
    Get all payments. Optionally filter by user_id and/or listing_id.
    """
    params = []
    if user_id is not None:
        params.append(f"user_id=eq.{user_id}")
    if listing_id is not None:
        params.append(f"listing_id=eq.{listing_id}")
    query = "&".join(params) if params else ""
    try:
        payments = await read_records(PAYMENTS_TABLE, query)
        return payments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_payment(payload: dict):
    """
    Create a payment record.
    Payload must include 'user_id', 'amount', 'listing_id'.
    """
    user_id = payload.get("user_id")
    listing_id = payload.get("listing_id")
    amount = payload.get("amount")
    if not user_id or not listing_id or amount is None:
        raise HTTPException(status_code=400, detail="user_id, listing_id, and amount are required.")

    await validate_user_and_listing(user_id, listing_id)

    payment_data = {
        "user_id": user_id,
        "listing_id": listing_id,
        "amount": amount,
        "confirmed": payload.get("confirmed", False),
        "created_at": datetime.utcnow().isoformat()
    }
    try:
        result = await create_record(PAYMENTS_TABLE, payment_data)
        return {"success": True, "msg": "Payment recorded.", "payment": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{payment_id}/confirm")
async def confirm_payment(payment_id: int):
    """
    Mark payment as confirmed.
    """
    try:
        await update_record(PAYMENTS_TABLE, f"id=eq.{payment_id}", {"confirmed": True})
        return {"success": True, "msg": "Payment confirmed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{payment_id}")
async def get_payment(payment_id: int):
    """
    Get a single payment by ID.
    """
    try:
        result = await read_records(PAYMENTS_TABLE, f"id=eq.{payment_id}")
        if not result:
            raise HTTPException(status_code=404, detail="Payment not found.")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/mpesa/webhook")
async def mpesa_webhook(request: Request):
    """
    M-PESA payment notification webhook.
    Expects JSON data from payment provider.
    """
    body = await request.json()
    print("Received M-PESA webhook:", body)
    # TODO: Validate, map, and update payments accordingly using CRUD helpers!
    return {"success": True}
