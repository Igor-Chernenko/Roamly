"""
Database.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ DataBase Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles Database connections 
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from config import settings

