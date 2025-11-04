import os
from dotenv import load_dotenv
import httpx

# --- Load environment variables for all database/Supabase config ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "listing-photos")  # Default bucket if not set

# --- Helper: Standard headers for Supabase HTTP requests ---
def get_supabase_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

# --- Optional: Shared HTTP client ---
# Use 'await client.aclose()' at shutdown if you leverage this singleton
client = httpx.AsyncClient()

# --- Usage Docs (for teammate or future you) ---
"""
How to use:

from database import (
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_BUCKET,
    get_supabase_headers,
    client,
)

- Use SUPABASE_URL, SUPABASE_KEY, etc. where you need URLs or keys.
- Use get_supabase_headers() to get standard headers for all httpx calls to Supabase.
- Use 'client' for making async HTTP calls if you want to re-use connections (optional).
"""
