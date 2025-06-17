"""
main.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Main Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles middleware, directing, 
anything you would excpect the main file to do
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.LLMdatapipeline.LLMutils import setup_qdrant
from app.routers import adventure, user, comments, images, chat

origins = [
    "http://localhost:8080",
    "http://localhost:3000",
    "http://localhost:6333",
    "http://127.0.0.1:3000",
    "http://3.23.70.81:80",
    "http://3.23.70.81:3000",
    "http://3.23.70.81",
    "http://roamly.quest",
    "http://www.roamly.quest"
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_qdrant()
    yield
    
app = FastAPI(lifespan=lifespan)

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

app.include_router(
	chat.router, 
	prefix="/chat",
	tags= ['Roamly-Rabbit']
	)