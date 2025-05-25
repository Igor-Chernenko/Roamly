"""
Database.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ DataBase Schema Layer ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

handles SQLalchemy Database Model Schema creation (Database strucuture)

Model Design Verion: 1.0
"""
from app.database import Base
from sqlalchemy import text, Column, Integer, String, Text, TIMESTAMP, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

#----------------------------------[ Users ]----------------------------------
"""
Data model for Users table in Database
    Collums:
        user_id: integer, primary key 
        username: string, unqique 
        email: string, unique
        password: string, unique, will be encrypted through hashing
        created_at: time, default= when created
"""
class Users(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key = True, nullable=False)
    username = Column(String, nullable = False, unique = True)
    email = Column(String, nullable = False, unique = True)
    password = Column(String, nullable = False)
    created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default= text("now()"))

    __table_args__ = (
    Index(
        "username_trgm_idx",
        "username",
        postgresql_using="gin",
        postgresql_ops={"username": "gin_trgm_ops"},
    ),
    )


#----------------------------------[ Adventures ]----------------------------------

"""
Data model for adventure table in Database
    Collums:
       adventure_id: int, primary_key
       title: string
       owner_id: int, 
       created_at: time, 
       Description: string, write about adventure

    Relationship to Users:
        Matches a user to the adventure based on the foreinKey Created

    Notes:
        Unique Constraint set to make the combination of title and owner_id unique
"""

class Adventures(Base):
    __tablename__ = "adventures"
    adventure_id = Column(Integer, nullable = False, primary_key = True)
    title = Column(String, nullable= False)
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete= "CASCADE"), nullable= False)
    created_at = Column(TIMESTAMP(timezone= True), nullable= False, server_default= text("now()"))
    description = Column(Text)

    owner = relationship("Users")

    __table_args__ = (
        UniqueConstraint('title', 'owner_id', name='uq_owner_title'),
        Index(
        "adventure_id_trgm_idx",
        "title",
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
        )
        )

#----------------------------------[ Likes ]----------------------------------

"""
Data model for Likes table in Database
    Collums:
       post_id, Primary_key, foreign key is the adventure id so if an adventure is deleted so is this like
       owner_id, Primary_key, foreign key is also the users id id so if a user is deleted so is this like

"""

class Likes(Base):
    __tablename__ = "likes"
    adventure_id = Column(Integer, ForeignKey("adventures.adventure_id", ondelete="CASCADE"), nullable = False, primary_key= True)
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable = False, primary_key= True)

#----------------------------------[ Images ]----------------------------------

"""
Data model for images table in Database, This will contain urls to AWS S3 for storage
    Collums:
    image_id, Primary key
    url, url to AWS S3
    adventure_id, int, foreign key to adventure id
    caption, str

"""

class Images(Base):
    __tablename__ = "images"
    image_id = Column(Integer, nullable=False, primary_key = True)
    url = Column(String, nullable = False, unique=True)
    adventure_id = Column(Integer, ForeignKey("adventures.adventure_id", ondelete="CASCADE"), nullable = False)
    caption = Column(String)
    owner_id = Column(Integer, nullable= False)

#----------------------------------[ Comments ]----------------------------------
"""
Data model for comments table in Database
    Collums:
    comment_id, int, primary key
    owner_id, int, foreign key to users.user_id
    created_at, time
    adventure_id, int, foreign key to adventures.adventure_id
    comment, string, main comment
"""
class Comments(Base):
    __tablename__ = "comments"
    comment_id = Column(Integer, primary_key=True, nullable = False)
    owner_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable = False)
    adventure_id = Column(Integer, ForeignKey("adventures.adventure_id", ondelete="CASCADE"), nullable = False)
    created_at = Column(TIMESTAMP(timezone=True),nullable = False, server_default=text("now()"))
    comment = Column(String, nullable = False)