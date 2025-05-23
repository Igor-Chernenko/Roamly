"""
images.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ comment Router ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles image CRUD operations for the api

Version 0.0.0
"""
from fastapi import APIRouter, HTTPException, status, Depends, Form, File,  UploadFile
from sqlalchemy.orm import Session
from typing import List
from random import randint

from app.schemas import ImageReturn, ImageChange
from app.models import Users as User, Adventures, Images
from app.oauth2 import get_gb, get_current_user

router = APIRouter()

#----------------------------------[ POST /image ]----------------------------------
"""
updates an adventures images by adding one

inputs: in Form Data
    - id of the adventure the image will be associated with
    - caption of the image
    - image data

returns:
    - HTTP 404 if the image id could not be found
    - HTTP 403 if the user is not the same as the owner of the image
    - if successfull then it returns a List of all images in adventure
"""
@router.post("/", response_model= List[ImageReturn])
async def post_image_adventure_id(
    adventure_id: int = Form(...),
    caption: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_gb),
    current_user: User = Depends(get_current_user)
):
    adventure = db.query(Adventures).filter(Adventures.adventure_id == adventure_id).first()
    if not adventure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"adventure with id={adventure_id} could not be found"
        )
    
    if adventure.owner_id != current_user.user_id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= f"You are not permitted to add photos to this adventure"
        )
    
    #S3url = await store_image(image) // to be implemented
    url_number = randint(1,9999)
    S3url = f"http://fake_url.com/{url_number}"

    new_image = Images(adventure_id = adventure_id, caption = caption, url= S3url, owner_id = current_user.user_id)
    db.add(new_image)
    db.commit()

    adventure_images = db.query(Images).filter(Images.adventure_id == adventure_id).all()
    return adventure_images

#----------------------------------[ GET /image ]----------------------------------
"""
Gets all of an adventures images

inputs: Id of the adventure

returns:
    - HTTP 404 if the Adventure couldnt be found
    - if successfull then it returns a List of all images in adventure

"""
@router.get("/{adventure_id}", response_model= List[ImageReturn])
async def get_image_id(adventure_id: int, db: Session = Depends(get_gb)):

    adventure = db.query(Adventures).filter(Adventures.adventure_id == adventure_id).first()
    if not adventure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"adventure with id={adventure_id} could not be found"
        )
    db_query = db.query(Images).filter(Images.adventure_id == adventure_id).all()
    return db_query


#----------------------------------[ DELETE /image ]----------------------------------
"""
delete a certain image

inputs: id of image you want to delete

returns:
    - HTTP 404 if the image id could not be found
    - HTTP 403 if the user is not the same as the owner of the image
    - if successfull then it returns a List of all images in adventure
"""
@router.delete("/{image_id}", status_code= status.HTTP_202_ACCEPTED, response_model= List[ImageReturn])
async def delete_id(image_id: int, db: Session = Depends(get_gb), current_user: User = Depends(get_current_user)):
    image_query = db.query(Images).filter(Images.image_id == image_id)
    image = image_query.first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"image with id={image_id} could not be found"
        )
    if current_user.user_id != image.owner_id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= f"You are not permitted to delete photos from this adventure"
        )
    adventure_id = image.adventure_id
    image_query.delete(synchronize_session= False)
    db.commit()
    return db.query(Images).filter(Images.adventure_id == adventure_id).all()
    

#----------------------------------[ PUT /comment ]----------------------------------
"""
Change an images caption

inputs: 
    - id of image you want to change
    - new caption of image

returns:
    - HTTP 404 if the image id could not be found
    - HTTP 403 if the user is not the same as the owner of the image
    - if successfull then it returns a List of all images in adventure
"""
@router.put("/{image_id}", response_model=List[ImageReturn])
async def put_image_id(image_id: int, new_caption: ImageChange, db: Session = Depends(get_gb), current_user: Session = Depends(get_current_user)):
    queried_images = db.query(Images).filter(Images.image_id == image_id)
    image = queried_images.first()

    if not image: 
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=f"image with id={image_id} could not be found"
        )
    
    if image.owner_id != current_user.user_id:
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail= f"You are not permitted to delete photos from this adventure"
        )
    
    adventure_id = image.adventure_id

    queried_images.update(
        new_caption.model_dump(),
        synchronize_session = False
    )

    db.commit()
    
    return db.query(Images).filter(Images.adventure_id == adventure_id)