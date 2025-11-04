from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import all_routers

app = FastAPI(
    title="KejaHunt API",
    description="FastAPI backend for KejaHunt property listing and landlord services, powered by Supabase.",
    version="1.0.0"
)

# CORS setup: allow frontend to access API
origins = [
    "http://localhost:3000",      # React dev server default
    "http://127.0.0.1:3000",     # Alternative localhost
    "http://localhost:5173",      # Vite dev server (React/Vue)
    "https://your-frontend-domain.com",  # Production frontend domain (replace with real domain)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Allowed frontend origins
    allow_credentials=True,      # Allow cookies, authorization headers
    allow_methods=["*"],         # Allow all HTTP methods (GET, POST, etc)
    allow_headers=["*"],         # Allow all headers
)

# Include all routers from routers/__init__.py
for router in all_routers:
    app.include_router(router)

@app.get("/")
async def root():
    return {"msg": "Welcome to the KejaHunt API"}
