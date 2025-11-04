import httpx
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

async def create_record(table: str, data: dict):
    """
    Create a new record in the specified Supabase table.
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=get_supabase_headers(), json=data)
    if resp.status_code not in (200, 201):
        raise Exception(f"Create failed: {resp.status_code} - {resp.text}")
    return resp.json()

async def read_records(table: str, query: str = "", select: str = "*"):
    """
    Read records from the specified Supabase table.
    `query` example: 'county_id=eq.2', 'role=eq.landlord'
    `select` example: 'id,email,role'
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}?select={select}"
    if query:
        url += f"&{query}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=get_supabase_headers())
    if resp.status_code != 200:
        raise Exception(f"Read failed: {resp.status_code} - {resp.text}")
    return resp.json()

async def update_record(table: str, query: str, data: dict):
    """
    Update records in the specified Supabase table.
    `query` example: 'id=eq.7'
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}?{query}"
    headers = get_supabase_headers()
    headers["Prefer"] = "resolution=merge-duplicates"
    async with httpx.AsyncClient() as client:
        resp = await client.patch(url, headers=headers, json=data)
    if resp.status_code not in (200, 204):
        raise Exception(f"Update failed: {resp.status_code} - {resp.text}")
    return True

async def delete_record(table: str, query: str):
    """
    Delete records from the specified Supabase table.
    `query` example: 'id=eq.17'
    """
    url = f"{SUPABASE_URL}/rest/v1/{table}?{query}"
    headers = get_supabase_headers()
    headers["Prefer"] = "return=representation"
    async with httpx.AsyncClient() as client:
        resp = await client.delete(url, headers=headers)
    if resp.status_code not in (200, 204):
        raise Exception(f"Delete failed: {resp.status_code} - {resp.text}")
    return True
