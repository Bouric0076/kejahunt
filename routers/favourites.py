from fastapi import APIRouter, HTTPException, Query
from .crud import read_records, create_record, delete_record

FAVOURITES_TABLE = "saved_listings"
LISTINGS_TABLE = "listings"

router = APIRouter(
    prefix="/favourites",
    tags=["favourites"]
)

@router.get("/")
async def get_favourites(
    user_id: int = Query(..., description="User ID to fetch favourites for")
):
    """
    Get all favourited listings for a user.
    """
    select = f"*,listing:{LISTINGS_TABLE}(*)"
    try:
        favourites = await read_records(FAVOURITES_TABLE, f"user_id=eq.{user_id}", select)
        return favourites
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def add_favourite(payload: dict):
    """
    Save (favourite) a listing for a user.
    Prevents duplicates.
    Payload must contain `user_id` and `listing_id`.
    """
    user_id = payload.get("user_id")
    listing_id = payload.get("listing_id")
    if not user_id or not listing_id:
        raise HTTPException(status_code=400, detail="user_id and listing_id required")

    try:
        # Check for existing favourite to prevent duplicates
        dups = await read_records(FAVOURITES_TABLE, f"user_id=eq.{user_id}&listing_id=eq.{listing_id}")
        if dups:
            raise HTTPException(status_code=409, detail="Listing is already in favourites.")
        await create_record(FAVOURITES_TABLE, payload)
        return {"success": True, "msg": "Favourite added."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/")
async def remove_favourite(
    user_id: int = Query(...), listing_id: int = Query(...)
):
    """
    Remove (un-favourite) a specific listing for a user.
    """
    if not user_id or not listing_id:
        raise HTTPException(status_code=400, detail="user_id and listing_id required")
    try:
        # Confirm it exists first
        dups = await read_records(FAVOURITES_TABLE, f"user_id=eq.{user_id}&listing_id=eq.{listing_id}")
        if not dups:
            raise HTTPException(status_code=404, detail="Favourite not found.")
        await delete_record(FAVOURITES_TABLE, f"user_id=eq.{user_id}&listing_id=eq.{listing_id}")
        return {"success": True, "msg": "Favourite removed."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
