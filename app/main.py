"""
main.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Main Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles middleware, directing, 
anything you would excpect the main file to do
"""

from fastapi import FastAPI
from app.routers import adventure, user

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


