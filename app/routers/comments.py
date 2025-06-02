"""
comment.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ comment Router ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=
handles comment CRUD operations for the api

"""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List

from app.models import Comments as Comment, Users as User, Adventures
from app.database import get_gb
from app.oauth2 import get_current_user
from app.schemas import CommentReturn, CommentPost

router = APIRouter()

#----------------------------------[ POST /comment/{adventure_id} ]----------------------------------
@router.post("/{adventure_id}/comments", status_code= status.HTTP_201_CREATED, response_model= CommentReturn)
async def post_comment(adventure_id: int, comment_data: CommentPost, db: Session= Depends(get_gb), current_user: User = Depends(get_current_user)):
    adventure_query = db.query(Adventures).filter(Adventures.adventure_id == adventure_id).first()
    if not adventure_query:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"could not find adventure with adventure id = {adventure_id}"
        )
    comment = Comment(
        **comment_data.model_dump(),
        adventure_id = adventure_id,
        owner_id = current_user.user_id
        )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return comment

#----------------------------------[ GET /comment ]----------------------------------
@router.get("/{adventure_id}/comments", status_code= status.HTTP_200_OK, response_model=List[CommentReturn])
def get_adventure_comments(adventure_id:int, db: Session = Depends(get_gb)):
    adventure_query = db.query(Adventures).filter(Adventures.adventure_id == adventure_id).first()
    if not adventure_query:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail= f"could not find adventure with adventure id = {adventure_id}"
        )
    comment_query = db.query(Comment).filter(Comment.adventure_id == adventure_id).all()
    return comment_query

#----------------------------------[ DELETE /comment ]----------------------------------
@router.delete("/comment/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment_id(comment_id:int, db:Session = Depends(get_gb), current_user: User = Depends(get_current_user)):
    comment_query = db.query(Comment).filter(Comment.comment_id ==  comment_id)
    comment = comment_query.first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id={comment_id} could not be found"
        )
    if current_user.user_id != comment.owner_id:
        raise HTTPException(
            status_code= status.HTTP_401_UNAUTHORIZED,
            detail= f"You are not permitted to delete comments from this adventure"
        )
    comment_query.delete(synchronize_session= False)
    db.commit()

#----------------------------------[ PUT /comment ]----------------------------------

#Currently the program does not call for updating comments