from fastapi import APIRouter, HTTPException, Query, Body
from .crud import read_records, create_record, update_record, delete_record

USERS_TABLE = "users"

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.get("/")
async def get_users(role: str = Query(None, description="Optional: filter by role (landlord/user)")):
    """
    Get all users (optional role filter).
    """
    query = f"role=eq.{role}" if role else ""
    try:
        users = await read_records(USERS_TABLE, query)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user_by_id(user_id: str):
    """
    Get user details by user ID.
    """
    try:
        results = await read_records(USERS_TABLE, f"id=eq.{user_id}")
        if not results:
            raise HTTPException(status_code=404, detail="User not found.")
        return results[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by_email/{email}")
async def get_user_by_email(email: str):
    """
    Get user details by email.
    """
    try:
        results = await read_records(USERS_TABLE, f"email=eq.{email}")
        if not results:
            raise HTTPException(status_code=404, detail="User not found.")
        return results[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{user_id}")
async def update_user(user_id: str, payload: dict = Body(...)):
    """
    Update a user's email or role.
    Payload can include: { "email": "...", "role": "user" | "landlord" }
    """
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update.")
    try:
        await update_record(USERS_TABLE, f"id=eq.{user_id}", payload)
        return {"success": True, "msg": "User updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    """
    Delete a user by ID (removes from users table; does NOT remove from Supabase Auth).
    """
    try:
        await delete_record(USERS_TABLE, f"id=eq.{user_id}")
        return {"success": True, "msg": "User deleted from table."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
