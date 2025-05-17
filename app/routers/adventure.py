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

from fastapi import HTTPException, status

router = APIRouter()
#----------------------------------[ GET /Adventures ]----------------------------------
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

#----------------------------------[ GET /Adventures/{id} ]----------------------------------
"""
Basic Get request to retreive Adventure data based on id

Input:
    id: searches for a specific adventure with matching id
    Example: http://localhost:8000/adventure/2
    
Return: Returns AdventureReturn pydantic schema if id is found
        Returns http exception with code 404 if adventure id is not found

"""
@router.get("/{id}",response_model=AdventureReturn)
async def get_adventure_id(id: int, db: Session = Depends(get_gb)):
    adventure_query = db.query(Adventures).filter(Adventures.adventure_id == id).first()
    
    if not adventure_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Adventure with id={id} could not be found"
        )
    
    return adventure_query

    
