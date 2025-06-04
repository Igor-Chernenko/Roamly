"""
adventure.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ adventure Router ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles Adventure CRUD operations for the api

"""

from fastapi import APIRouter, Depends
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from app.database import get_gb
from sqlalchemy import func, desc
import tempfile
import os
import boto3
from botocore.exceptions import ClientError
from urllib.parse import urlparse

from app.schemas import AdventureReturn, AdventureUpdate
from app.models import Adventures, Images, Users
from app.oauth2 import get_current_user
from app.aws import upload_file
from app.config import settings


from fastapi import HTTPException, status, UploadFile, File, Form

router = APIRouter()

#----------------------------------[ GET /adventures ]----------------------------------
"""
Basic Get request to retrieve Adventure data

Input:
    limit: limit the amount of objects returned
    skip: skips a certain amount of adventures
    search: searches for a keyword in titles of Adventures
    Example: http://localhost:8000/adventure/?limit=2&search=hiking
    
Return: Returns list of AdventureReturn pydantic schemas 

"""
@router.get("/",response_model = List[AdventureReturn])
async def get_adventure(db: Session = Depends(get_gb), limit:int=5, skip:int = 0, search:Optional[str]=None):
    if limit<1:
        raise HTTPException(
            status_code= status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail= "limit parameter may not be less than 1 if included"
        )
    if search:
        similarity_amount = 0.2
        adventures = (
            db.query(Adventures)
            .filter(func.similarity(Adventures.title, search) > similarity_amount)
            .order_by(func.similarity(Adventures.title, search).desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return adventures
    
    else:
        queried_adventures = (
            db.query(Adventures)
            .order_by(desc(Adventures.created_at))
            .limit(limit)
            .offset(skip)
            .all()
        )
        return queried_adventures

#----------------------------------[ GET /adventures/{id} ]----------------------------------
"""
Basic Get request to retrieve Adventure data based on id

Input:
    id: searches for a specific adventure with matching id
    Example: http://localhost:8000/adventure/2
    
Return: Returns AdventureReturn pydantic schema if id is found
        Returns http exception with code 404 if adventure id is not found

"""
@router.get("/{id}",response_model=AdventureReturn)
async def get_adventure_id(id: int, db: Session = Depends(get_gb)):
    adventure_query = db.query(Adventures).filter(Adventures.adventure_id == id).first()
    if id<1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"id cannot be less than 1"
        )
    if not adventure_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Adventure with id={id} could not be found"
        )
    
    return adventure_query

#----------------------------------[ POST /adventures ]----------------------------------
"""
Post request to create Adventure Post

Input:
    title: Title of the adventure (Text)
    description: Description of the adventure (Text)
    Images: List of the images of uploaded to the adventure
    Caption: List of the Captions of each picture (empty string if no caption)
    Users information

Return: if successfull: Returns HTTP 201 and AdventureReturn pydantic Schema
        if not successfull:
            - Raises HTTP 422 if amount of caption inputs and Image inputs doesnt match

Notes about how this works:
    The api receives the request in multipart/form-data form, fastapi reads the boundary,
    seperates the data by the boundery and confirms that the content name matches each
    input. Image is stored in an UploadFile type and avoids writing the entire image into 
    memory.

    The adventure is then written into an Adventures model which is then uploaded to POSTGRES,
    the database writes the data and then returns with the updated data

    

PLAN: EXPORT THE DATA INTO S3 AND UPLOAD URL INTO IMAGES DATABASE, CURRENTLY NOT IMPLEMENTED


"""
from random import randint

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= AdventureReturn)
async def post_adventure_create(
    title:str = Form(...),
    description: str = Form(...),
    images: List[UploadFile] = File(...),
    caption: List[str] = Form(...),
    db: Session = Depends(get_gb),
    current_user: Users = Depends(get_current_user)
):
    if len(title) < 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="There must be at least 5 characters in the title"
        )
    
    num_valid_captions = 0
    for cap in caption:
        if len(cap) >0 :
            num_valid_captions+=1

    if len(images) != num_valid_captions:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Number of image files must match number of captions"
        )
    if len(images) >10:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Number of image files must be under or equal to 10"
        )

    #do a check if title and owner_id already exists
    title_check = db.query(Adventures).filter(Adventures.title == title and Adventures.owner_id == current_user.user_id).first()
    if title_check:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail="User has already posted an adventure with this title"
        )

    new_adventure = Adventures(title=title, description=description, owner_id = current_user.user_id)
    db.add(new_adventure)
    db.commit()
    db.refresh(new_adventure)

    for i, image in enumerate(images):
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(await image.read())
            tmp_path = tmp.name

        # Generate random object name
        object_name = f"adventures/{new_adventure.adventure_id}/{randint(1,999999)}_{image.filename}"

        # Upload to S3
        upload_success = upload_file(tmp_path, settings.S3_BUCKET_NAME, object_name)
        os.remove(tmp_path)

        if not upload_success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image to S3"
            )

        S3url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{object_name}"

        new_image = Images(
            url=S3url,
            caption=caption[i],
            adventure_id=new_adventure.adventure_id,
            owner_id=current_user.user_id
        )
        db.add(new_image)
    db.commit()

    return new_adventure

#----------------------------------[ DELETE /adventures/{id} ]----------------------------------
"""
Delete request to delete an adventure based off of id

Input:
    id: id of adventure to delete

Process:
    -Check if user attempting to delete is the same as the owener of the post
Return:
    - if found and deleted successfully: HTTP status code 204 with no return Content
    - if not found: HTTP status code 404
    - if person accessing is not the owner of post: HTTP status code 403
"""
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_adventure_id(id: int, db: Session = Depends(get_gb), current_user: Users = Depends(get_current_user)):
    
    queried_adventure = db.query(Adventures).filter(Adventures.adventure_id == id)
    adventure = queried_adventure.first()

    if adventure == None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"Adventure with id={id} could not be found"
        )
    
    if adventure.owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )
    
    images = db.query(Images).filter(Images.adventure_id == id).all()
    s3 = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

    for image in images:
        try:
            parsed = urlparse(image.url)
            bucket = parsed.netloc.split('.')[0]
            key = parsed.path.lstrip('/')
            s3.delete_object(Bucket=bucket, Key=key)
        except ClientError as e:
            print(f"Warning: could not delete {image.url} from S3: {e}")

    #  Remove images from the database
    db.query(Images).filter(Images.adventure_id == id).delete()
    
    queried_adventure.delete(synchronize_session= False)
    db.commit()

#----------------------------------[ PUT /adventures/{id} ]----------------------------------
"""
PUT request to update an adventure based off of id

Input:
    id: id of adventure to update

Return:
    - if found and updated successfully: HTTP status code 204 with no return Content
    - if not found: HTTP status code 404
   - if person accessing is not the owner of post: HTTP status code 403

notes:
    -Only changes the inputs recieved, must be in json format
"""
@router.put("/{id}", status_code= status.HTTP_204_NO_CONTENT)
async def update_adventure_id(id: int, new_adventure: AdventureUpdate, db: Session = Depends(get_gb), current_user: Users = Depends(get_current_user)):
    queried_adventure = db.query(Adventures).filter(Adventures.adventure_id == id)

    update_data = new_adventure.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no data provided for update"
    )

    if new_adventure.title:
        title_query = db.query(Adventures).filter(
        (Adventures.title == new_adventure.title) & (Adventures.owner_id == current_user.user_id)
        ).first()

        if title_query:
            raise HTTPException(
                status_code= status.HTTP_409_CONFLICT,
                detail= "User has already made an adventure with this title"
            )
    
    if queried_adventure.first() == None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"Adventure with id={id} could not be found"
        )

    if queried_adventure.first().owner_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permision to perform this action"
        )

    queried_adventure.update(
        new_adventure.model_dump(exclude_unset=True),
        synchronize_session = False
    )

    db.commit()

