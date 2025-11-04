from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# --- User Schemas ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str = Field(..., regex="^(landlord|user)$")

class UserOut(BaseModel):
    id: str
    email: EmailStr
    role: str

# --- Login/Register Schemas ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(UserCreate):
    pass

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- County Schemas ---
class CountyCreate(BaseModel):
    name: str

class CountyOut(BaseModel):
    id: int
    name: str

# --- Region Schemas ---
class RegionCreate(BaseModel):
    name: str
    county_id: int

class RegionOut(BaseModel):
    id: int
    name: str
    county_id: int

# --- Listing Schemas ---
class ListingCreate(BaseModel):
    title: str
    type: str
    price: float
    region_id: int
    description: Optional[str] = None

class ListingOut(BaseModel):
    id: int
    title: str
    type: str
    price: float
    region_id: int
    description: Optional[str] = None
    photos: Optional[List[dict]] = None

# --- Photo Schemas ---
class PhotoCreate(BaseModel):
    listing_id: int
    url: str

class PhotoOut(BaseModel):
    id: int
    listing_id: int
    url: str

# --- Payment Schemas ---
class PaymentCreate(BaseModel):
    user_id: int
    listing_id: int
    amount: float
    confirmed: bool = False

class PaymentOut(BaseModel):
    id: int
    user_id: int
    listing_id: int
    amount: float
    confirmed: bool

# --- Favourites Schemas ---
class FavouriteCreate(BaseModel):
    user_id: int
    listing_id: int

class FavouriteOut(BaseModel):
    id: int
    user_id: int
    listing_id: int

# --- General Response Support ---
class ResponseMessage(BaseModel):
    success: bool
    msg: Optional[str] = None
