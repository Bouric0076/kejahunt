from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from .crud import read_records
import os
from dotenv import load_dotenv

# Load .env variables for local dev
load_dotenv()

LISTINGS_TABLE = "listings"

router = APIRouter(
    prefix="/listings",
    tags=["listings"]
)

@router.get("/")
async def get_listings(
    skip: int = 0,
    limit: int = 20,
    county_id: Optional[int] = Query(None, description="Filter by county id"),
    region_id: Optional[int] = Query(None, description="Filter by region id"),
    price_min: Optional[float] = Query(None, description="Minimum price"),
    price_max: Optional[float] = Query(None, description="Maximum price"),
    type: Optional[str] = Query(None, description="Filter by house type (e.g. bedsitter, 1BR, 2BR)"),
):
    """
    Get a list of property listings with optional filters.
    """
    # Construct filters
    filters = []
    if county_id is not None:
        filters.append(f"region_id=in.(select id from regions where county_id=eq.{county_id})")
    if region_id is not None:
        filters.append(f"region_id=eq.{region_id}")
    if price_min is not None:
        filters.append(f"price=gte.{price_min}")
    if price_max is not None:
        filters.append(f"price=lte.{price_max}")
    if type is not None:
        filters.append(f"type=eq.{type}")

    query = "&".join(filters)
    select = "*,photos(*),regions(*),counties(*)"
    query_str = query
    # Add limit and offset for pagination
    if query_str:
        query_str += f"&limit={limit}&offset={skip}"
    else:
        query_str = f"limit={limit}&offset={skip}"

    try:
        listings = await read_records(LISTINGS_TABLE, query_str, select)
        return listings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{listing_id}")
async def get_listing(listing_id: int):
    """
    Get details for a single house listing.
    """
    select = "*,photos(*),regions(*),counties(*)"
    try:
        results = await read_records(LISTINGS_TABLE, f"id=eq.{listing_id}", select)
        if not results:
            raise HTTPException(status_code=404, detail="Listing not found")
        return results[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
