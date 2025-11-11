# KejaHunt Backend

# Overview
KejaHunt is a property listing platform backend built with FastAPI.
It provides RESTful APIs for property listing management, user authentication, photo uploading, payments, and more. The backend is tightly integrated with Supabase for database, storage, and authentication.

# Features
User authentication (sign-up, login, JWT, roles)

CRUD for listings, users, regions, counties, and favourites

Photo uploads to Supabase Storage

Payments integration (with webhook placeholder)

Automated landlord reminders via FastMail

CORS support for frontend apps

# Technologies
Python (FastAPI, Pydantic)

Supabase (PostgreSQL, Auth, Storage)

Async HTTP (httpx)

JWT tokens

Email (FastMail)

Docker support (optional)

Git & CI/CD ready

# Project Structure

backend/

│

├── main.py           # FastAPI app entrypoint, CORS setup, includes routers

├── database.py       # Supabase config, HTTP helpers

├── models.py         # Pydantic models for entities

├── schemas.py        # Additional Pydantic schemas

├── .env              # Secret keys and DB connection (never push this!)

├── routers/
│   ├── __init__.py     # Aggregates all routers

│   ├── crud.py         # Async CRUD helpers for Supabase API

│   ├── regions.py      # API for regions

│   ├── users.py        # API for users

│   ├── listings.py     # API for listings

│   ├── photos.py       # API for photo uploads/fetching

│   ├── payments.py     # API for payments/webhook

│   ├── favourites.py   # API for saved listings

│   ├── counties.py     # API for counties

│   ├── auth.py         # Authentication endpoints

└── .gitignore        # Makes sure secrets/dev files are NOT committed

# Common Endpoints
Path	Method	Description

/auth/register	POST	User signup

/auth/login	POST	User login/JWT

/listings/	GET	Fetch listings

/listings/	POST	Create listing

/photos/upload	POST	Upload listing photo

/payments/	POST	Create a payment

/regions/	GET	Get all regions

/users/	GET	Get all users

# Authors
Josphat Munene

Bouric Okwaro

Daniel Bundi
