"""
post.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ post Router ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles post CRUD operations for the api

Version 0.13
"""

from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.database import get_gb

from app.schemas import AdventureReturn
from app.models import Adventures, Images, Users

from fastapi import HTTPException, status, UploadFile, File, Form

router = APIRouter()
#----------------------------------[ GET /adventures ]----------------------------------
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

#----------------------------------[ GET /adventures/{id} ]----------------------------------
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

#----------------------------------[ POST /adventures/create ]----------------------------------
"""
Post request to create Adventure Post

Input:
    title: Title of the adventure (Text)
    description: Description of the adventure (Text)
    Images: List of the images of uploaded to the adventure
    Caption: List of the Captions of each picture (empty string if no caption)

Return: if successfull: Returns HTTP 201 and AdventureReturn pydantic Schema
        if not successfull:
            - Raises HTTP 422 if amount of caption inputs and Image inputs doesnt match

Notes about how this works:
    The api recieves the request in multipart/form-data form, fastapi reads the boundry,
    seperates the data by the boundery and confirms that the content name matches each
    input. Image is stored in an UploadFile type and avoids writing the entire image into 
    memory.

    The adventure is then written into an Adventures model which is then uploaded to POSTGRES,
    the database writes the data and then returns with the updated data

    

PLAN: EXPORT THE DATA INTO S3 AND UPLOAD URL INTO IMAGES DATABASE, CURRENTLY NOT IMPLEMENTED


"""
from random import randint

@router.post("/create", status_code= status.HTTP_201_CREATED, response_model= AdventureReturn)
async def post_adventure_create(
    title:str = Form(...),
    description: str = Form(...),
    images: List[UploadFile] = File(...),
    caption: List[str] = Form(...),
    db: Session = Depends(get_gb)
):
    
    if len(images) != len(caption):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Number of image files must match number of captions"
        )

    temp_user_id = 1

    new_adventure = Adventures(title=title, description=description, owner_id = temp_user_id)
    db.add(new_adventure)
    db.commit()
    db.refresh(new_adventure)

    for i, image in enumerate(images):
        #S3url = await store_image(image) // to be implemented
        url_number = randint(1,9999)
        S3url = f"http://fake_url.com/{url_number}"
        new_image= Images(
            url = S3url,
            caption = caption[i],
            adventure_id = new_adventure.adventure_id
            )
        db.add(new_image)
        db.commit()
        db.refresh(new_image)

    return new_adventure