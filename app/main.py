"""
main.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Main Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles middleware, directing, 
anything you would excpect the main file to do
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import adventure, user, comments, images

origins = [
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
	adventure.router, 
	prefix="/adventure",
	tags= ['Adventures'] #for documentation grouping
	)

app.include_router(
	user.router, 
	prefix="/user",
	tags= ['Users']
	)

app.include_router(
    comments.router, 
    prefix="/adventure",
    tags=['Comments']
)

app.include_router(
	images.router, 
	prefix="/adventure",
	tags= ['Images']
	)
