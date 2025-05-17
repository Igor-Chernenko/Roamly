"""
post.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ post Router ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles post CRUD operations for the api
"""

from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.database import get_gb

from app.schemas import AdventureReturn
from app.models import Adventures, Users
router = APIRouter()
#----------------------------------[ GET ]----------------------------------
"""
Basic Get request to retreive Adventure data

Input:
    limit: limit the amount of objects returned
    skip: skips a certain amount of adventures
    search: searches for a keyword in titles of Adventures
    Example: http://localhost:8000/adventure/?limit=2&search=hiking
    
Return: Returns list of AdventureReturn pydantic schemas 

"""
@router.get("/",response_model=List[AdventureReturn])
async def get_adventure(db: Session = Depends(get_gb), limit:int=5, skip:int = 0, search:Optional[str]=None):
    
    if search:
        queried_adventures = (
            db.query(Adventures)
            .filter(Adventures.title.contains(search))
            .limit(limit)
            .offset(skip)
            .all()
        )
    else:
        queried_adventures = (
            db.query(Adventures)
            .limit(limit)
            .offset(skip)
            .all()
        )
    
    return queried_adventures