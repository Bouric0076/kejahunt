from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    role: str = Field(..., regex="^(landlord|user)$")

class UserCreate(UserBase):
    password: str  # Only for registration

class UserResponse(UserBase):
    id: str

# --- Region Schemas ---
class RegionBase(BaseModel):
    name: str
    county_id: int

class RegionCreate(RegionBase):
    pass

class RegionResponse(RegionBase):
    id: int

# --- County Schemas ---
class CountyBase(BaseModel):
    name: str

class CountyCreate(CountyBase):
    pass

class CountyResponse(CountyBase):
    id: int

# --- Listing Schemas ---
class ListingBase(BaseModel):
    title: str
    type: str
    price: float
    region_id: int
    description: Optional[str] = None

class ListingCreate(ListingBase):
    pass

class ListingResponse(ListingBase):
    id: int
    photos: Optional[list] = None

# --- Photo Schemas ---
class PhotoBase(BaseModel):
    url: str
    listing_id: int

class PhotoUpload(PhotoBase):
    pass

class PhotoResponse(PhotoBase):
    id: int

# --- Payment Schemas ---
class PaymentBase(BaseModel):
    user_id: int
    listing_id: int
    amount: float
    confirmed: bool = False

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: int

# --- Favourites Schemas ---
class FavouriteBase(BaseModel):
    user_id: int
    listing_id: int

class FavouriteCreate(FavouriteBase):
    pass

class FavouriteResponse(FavouriteBase):
    id: int

# --- Auth ---
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
