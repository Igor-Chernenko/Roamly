"""
test_adventure.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Tests for adventure Endpoints ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

"""
from fastapi import status, HTTPException
from app import schemas
from app import models
from app import oauth2

import pytest
#----------------------------------[ TEST GET /adventures ]----------------------------------

def test_get_adventure(client, test_adventures):
    result = client.get("adventure/")
    assert len(result.json()) == 4
    assert result.status_code == status.HTTP_200_OK

def test_get_adventure_with_parameters(client, test_adventures):
    parameters = {
        "limit": 2,
        "skip" : 1
    }

    result = client.get(f"adventure/", params=parameters)
    assert len(result.json()) == 2
    assert result.status_code == status.HTTP_200_OK
    adventure = result.json()[0]
    assert adventure['title'] == 'new adventure part 2'
    assert adventure['description'] == 'adventure description 2'
    assert adventure['adventure_id'] == 2
    assert adventure['owner']['email'] == "test_user@gmail.com"
    
def test_get_adventure_with_fuzzy_search(client, test_adventures):
    parameters = {
        "search": " part "
    }
    result = client.get(f"adventure/", params=parameters)
    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()) == 3

def test_get_adventure_with_invalid_fuzzy_search(client, test_adventures):
    parameters = {
        "search": " Pumpernickel "
    }
    result = client.get(f"adventure/", params=parameters)
    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()) == 0

def test_get_adventure_invalid_limit(client):
    result = client.get("/adventure/", params={"limit": -1})
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY



#----------------------------------[ TEST POST /adventures ]----------------------------------

def test_posting_adventure(client, session, test_adventures, test_user):
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    data = {
        "title": "hiking the Juan de Fuca Trail with friends!",
        "description": "got to go on an amazing trail with my friends!",
        "caption": ["at the trailhead", "great views all around", "saw a bird", "at the end"]
    }

    files = [
        ("images", ("image1.jpg", b"file_content_1", "image/jpeg")),
        ("images", ("image2.jpg", b"file_content_2", "image/jpeg")),
        ("images", ("image3.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image4.jpg", b"file_content_4", "image/jpeg")),
    ]

    
    result = client.post("/adventure/", data=data, files=files, headers=jwt)
    assert result.status_code == status.HTTP_201_CREATED
    response = schemas.AdventureReturn(**result.json())
    assert response.title == 'hiking the Juan de Fuca Trail with friends!'
    assert response.description == 'got to go on an amazing trail with my friends!'
    assert response.adventure_id == 5
    image_query = session.query(models.Images).filter(models.Images.adventure_id == 5).all()
    assert len(image_query) == 4

def test_invalid_adventure_too_few_captions(client, test_adventures, test_user):
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    data = {
        "title": "hiking the Juan de Fuca Trail with friends!",
        "description": "got to go on an amazing trail with my friends!",
        "caption": ["at the trailhead", "saw a bird", "at the end"]
    }

    files = [
        ("images", ("image1.jpg", b"file_content_1", "image/jpeg")),
        ("images", ("image2.jpg", b"file_content_2", "image/jpeg")),
        ("images", ("image3.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image4.jpg", b"file_content_4", "image/jpeg")),
    ]
    result = client.post("/adventure/", data=data, files=files, headers=jwt)
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

def test_invalid_adventure_too_few_images(client, test_adventures, test_user):
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    data = {
        "title": "hiking the Juan de Fuca Trail with friends!",
        "description": "got to go on an amazing trail with my friends!",
        "caption": ["at the trailhead", "great views all around", "saw a bird", "at the end"]
    }

    files = [
        ("images", ("image1.jpg", b"file_content_1", "image/jpeg")),
        ("images", ("image2.jpg", b"file_content_2", "image/jpeg")),
        ("images", ("image3.jpg", b"file_content_3", "image/jpeg")),
    ]
    result = client.post("/adventure/", data=data, files=files, headers=jwt)
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_invalid_adventure_duplicate_title(client, test_user,  test_adventures):
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    data = {
        "title": "new adventure part 1",
        "description": "got to go on an amazing trail with my friends!",
        "caption": ["at the trailhead", "great views all around", "saw a bird"]
    }

    files = [
        ("images", ("image1.jpg", b"file_content_1", "image/jpeg")),
        ("images", ("image2.jpg", b"file_content_2", "image/jpeg")),
        ("images", ("image3.jpg", b"file_content_3", "image/jpeg")),
    ]
    result = client.post("/adventure/", data=data, files=files, headers=jwt)
    assert result.status_code == status.HTTP_409_CONFLICT

def test_too_many_images(client, test_adventures, test_user):
    #max is currently 10
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    data = {
        "title": "new adventure part 1",
        "description": "got to go on an amazing trail with my friends!",
        "caption": [
            "caption1",
            "caption2",
            "caption3",
            "caption4",
            "caption5",
            "caption6",
            "caption7",
            "caption8",
            "caption9",
            "caption10",
            "caption11"
        ]
    }

    files = [
        ("images", ("image1.jpg", b"file_content_1", "image/jpeg")),
        ("images", ("image2.jpg", b"file_content_2", "image/jpeg")),
        ("images", ("image3.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image4.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image5.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image6.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image7.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image8.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image9.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image10.jpg", b"file_content_3", "image/jpeg")),
        ("images", ("image11.jpg", b"file_content_3", "image/jpeg"))
    ]
    result = client.post("/adventure/", data=data, files=files, headers=jwt)
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert result.json().get('detail') == "Number of image files must be under or equal to 10"
#----------------------------------[ TEST GET /adventures/{id} ]----------------------------------
def test_get_adventure_id(client, test_user, test_adventures):
    result = client.get(f"adventure/{1}")
    assert result.status_code == status.HTTP_200_OK
    response = schemas.AdventureReturn(**result.json())
    assert response.adventure_id == 1
    assert response.title == "new adventure part 1"

def test_get_invalid_adventure_id(client, test_user, test_adventures):
    result = client.get(f"adventure/{id}")
    assert result.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

#----------------------------------[ TEST DELETE /adventures/{id} ]----------------------------------
def test_delete_adventure_id(client, test_user, session, test_adventures):
    id = test_user["user_id"]
    jwt = {"Authorization" : f"bearer {test_user["jwt_token"]}"}
    result = client.delete(f"/adventure/{1}", headers= jwt)
    assert result.status_code == status.HTTP_204_NO_CONTENT
    user_query = session.query(models.Adventures).filter(models.Adventures == id).first()
    assert not user_query

def test_unauthorized_delete_adventure(client, test_user, session, test_adventures):
    bad_id = 2
    bad_access_token = oauth2.create_access_token(data = {"user_id":bad_id})
    jwt = {"Authorization" : f"bearer {bad_access_token}"}
    result = client.delete(f"/adventure/{1}", headers= jwt)
    assert result.status_code == status.HTTP_403_FORBIDDEN

def test_no_jwt_delete(client, test_user, session, test_adventures):
    result = client.delete(f"/adventure/{1}")
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

def test_expired_jwt_delete(client, test_user, session, test_adventures):
    id = 1
    expired_access_token = oauth2.create_access_token(data = {"user_id":id}, testing_state= True)
    jwt = {"Authorization" : f"bearer {expired_access_token}"}
    result = client.delete(f"/adventure/{1}", headers= jwt)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

def test_delete_nonexistent_adventure(client, test_user):
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}
    result = client.delete("/adventure/999", headers=jwt)
    assert result.status_code == status.HTTP_404_NOT_FOUND

#----------------------------------[ TEST PUT /adventures/{id} ]----------------------------------
@pytest.mark.parametrize("title, description",[
    (None, "new_description"),
    ("new_title", None),
    ("new_title", "new_description")
])
def test_update_adventure_id(client, test_user, session, test_adventures, title, description):
    adventure_id = 1
    update_json ={}
    jwt = {"Authorization" : f"bearer {test_user["jwt_token"]}"}
    if title:
        update_json["title"] = title
    if description:
        update_json["description"] = description

    result = client.put(f"adventure/{adventure_id}", json= update_json, headers= jwt)
    assert result.status_code == status.HTTP_204_NO_CONTENT

@pytest.mark.parametrize("title, description, status_code",[
    (None, "", status.HTTP_400_BAD_REQUEST),
    ("", None, status.HTTP_400_BAD_REQUEST),
    (None, None, status.HTTP_400_BAD_REQUEST),
    ("", "", status.HTTP_400_BAD_REQUEST),
    ("new adventure part 2", None, status.HTTP_409_CONFLICT) #duplicate check
])
def test_invalid_update_adventure_id(client, test_user, session, test_adventures, title, description, status_code):
    adventure_id = 1
    update_json ={}
    jwt = {"Authorization" : f"bearer {test_user["jwt_token"]}"}
    if title:
        update_json["title"] = title
    if description:
        update_json["description"] = description

    result = client.put(f"adventure/{adventure_id}", json= update_json, headers= jwt)
    assert result.status_code == status_code


def test_no_jwt_update(client, test_user, session, test_adventures):
    adventure_id = 1
    update_json ={
        "title":"new_title",
        "description": "new_description"
    }
    result = client.put(f"/adventure/{adventure_id}", json=update_json)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

def test_expired_jwt_update(client, test_user, session, test_adventures):
    adventure_id = 1
    update_json ={
        "title":"new_title",
        "description": "new_description"
    }
    id = 1
    expired_access_token = oauth2.create_access_token(data = {"user_id":id}, testing_state= True)
    jwt = {"Authorization" : f"bearer {expired_access_token}"}

    result = client.put(f"adventure/{adventure_id}", json= update_json, headers= jwt)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

def test_update_unauthorized_user(client, test_user, test_adventures):
    bad_user_id = 2
    jwt = {"Authorization": f"bearer {oauth2.create_access_token({'user_id': bad_user_id})}"}
    update_json = {"title": "unauthorized title update"}

    result = client.put("/adventure/1", json=update_json, headers=jwt)
    assert result.status_code == status.HTTP_403_FORBIDDEN

def test_update_nonexistent_adventure(client, test_user):
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}
    update_json = {"title": "some title", "description": "some desc"}

    result = client.put("/adventure/999", json=update_json, headers=jwt)
    assert result.status_code == status.HTTP_404_NOT_FOUND

