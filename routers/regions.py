from fastapi import APIRouter, HTTPException, Query
from .crud import read_records, create_record
# If you want to support updates/deletes later, import update_record, delete_record

REGIONS_TABLE = "regions"

router = APIRouter(
    prefix="/regions",
    tags=["regions"]
)

@router.get("/")
async def get_regions(county_id: int = Query(None, description="Filter regions by county_id")):
    """
    Retrieve all regions. Optional county_id filter.
    """
    query = f"county_id=eq.{county_id}" if county_id is not None else ""
    try:
        regions = await read_records(REGIONS_TABLE, query)
        return regions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{region_id}")
async def get_region(region_id: int):
    """
    Get details for a single region by its ID.
    """
    try:
        result = await read_records(REGIONS_TABLE, f"id=eq.{region_id}")
        if not result:
            raise HTTPException(status_code=404, detail="Region not found.")
        return result[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def add_region(payload: dict):
    """
    Add a new region. Payload: { "name": "...", "county_id": ... }
    Prevents duplicates within same county.
    """
    name = payload.get("name")
    county_id = payload.get("county_id")
    if not name or not county_id:
        raise HTTPException(status_code=400, detail="Both name and county_id are required.")

    try:
        # Prevent duplicates by name within the same county
        dups = await read_records(REGIONS_TABLE, f"name=eq.{name}&county_id=eq.{county_id}")
        if dups:
            raise HTTPException(status_code=409, detail="Region with this name already exists in the county.")
        await create_record(REGIONS_TABLE, {"name": name, "county_id": county_id})
        return {"success": True, "msg": "Region added successfully."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
