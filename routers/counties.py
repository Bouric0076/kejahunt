from fastapi import APIRouter, HTTPException
from .crud import read_records, create_record

COUNTIES_TABLE = "counties"

router = APIRouter(
    prefix="/counties",
    tags=["counties"]
)

@router.get("/")
async def get_counties():
    """
    Get all counties in Kenya.
    """
    try:
        counties = await read_records(COUNTIES_TABLE)
        return counties
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{county_id}")
async def get_county(county_id: int):
    """
    Get details for a single county by ID.
    """
    try:
        result = await read_records(COUNTIES_TABLE, f"id=eq.{county_id}")
        if not result:
            raise HTTPException(status_code=404, detail="County not found.")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def add_county(payload: dict):
    """
    Add a new county (admin only).
    Payload should include 'name'.
    """
    name = payload.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="County name required.")
    try:
        # Optionally check for duplicates before adding
        dups = await read_records(COUNTIES_TABLE, f"name=eq.{name}")
        if dups:
            raise HTTPException(status_code=409, detail="County name already exists.")
        await create_record(COUNTIES_TABLE, {"name": name})
        return {"success": True, "msg": "County added successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
