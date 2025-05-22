"""
main.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Main Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles middleware, directing, 
anything you would excpect the main file to do
"""

from fastapi import FastAPI
from app.routers import adventure, user, comments, images

app = FastAPI()

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
	prefix="/comment",
	tags= ['Comments']
	)

app.include_router(
	images.router, 
	prefix="/image",
	tags= ['Images']
	)



