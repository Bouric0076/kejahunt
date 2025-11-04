from .regions import router as regions_router
from .users import router as users_router
from .photos import router as photos_router
from .payments import router as payments_router
from .listings import router as listings_router
from .favourites import router as favourites_router
from .counties import router as counties_router
from .auth import router as auth_router

# Note: crud.py provides helpers, not a router, so do NOT include it in the list below!

all_routers = [
    regions_router,
    users_router,
    photos_router,
    payments_router,
    listings_router,
    favourites_router,
    counties_router,
    auth_router
]
