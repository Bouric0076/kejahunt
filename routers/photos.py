from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from .crud import read_records, create_record, delete_record
import httpx
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "listing-photos")  # Supabase storage bucket name
PHOTOS_TABLE = "photos"

router = APIRouter(
    prefix="/photos",
    tags=["photos"]
)

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

@router.post("/upload/")
async def upload_photo(
    listing_id: int = Form(...),
    file: UploadFile = File(...)
):
    """
    Uploads an image file for a property listing; saves public URL in photos table.
    """
    # Save to Supabase Storage
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    storage_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{filename}"
    file_content = await file.read()

    headers = get_supabase_headers()
    headers.pop("Content-Type")  # Required for multipart upload

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            storage_url,
            headers=headers,
            content=file_content
        )
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=resp.status_code, detail=f"Upload failed: {resp.text}")

    # Make public URL (depends on your Supabase settings, check your bucket/policy config)
    public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{filename}"

    # Store photo record in photos table using CRUD helper
    photo_info = {
        "listing_id": listing_id,
        "url": public_url
    }
    try:
        result = await create_record(PHOTOS_TABLE, photo_info)
        return {"success": True, "url": public_url, "photo": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_photos(listing_id: int = None):
    """
    Get all photo records, or all photos for a specific listing.
    """
    query = f"listing_id=eq.{listing_id}" if listing_id else ""
    try:
        photos = await read_records(PHOTOS_TABLE, query)
        return photos
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{photo_id}")
async def delete_photo(photo_id: int):
    """
    Delete a photo by its record ID (removes from DB but not from storage for simplicity).
    """
    try:
        await delete_record(PHOTOS_TABLE, f"id=eq.{photo_id}")
        return {"success": True, "msg": "Photo deleted from photos table."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
