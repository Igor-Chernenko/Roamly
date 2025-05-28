"""
test_images.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Tests for Images Endpoints ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

"""
import pytest
from fastapi import status
from app import models
from app import schemas
from app.oauth2 import create_access_token
#----------------------------------[ TEST POST /image ]----------------------------------

@pytest.mark.parametrize("adventure_id, caption, image", [
    (1, "nice view", ("image.jpg", b"file_content_1", "image/jpeg")),
    (1, "", ("image.jpg", b"file_content_1", "image/jpeg")),
    (1, "nice view", ("image.png", b"file_content_1", "image/png")),
    (1, "nice view", ("image.webp", b"file_content_1", "image/webp")),
])
def test_post_image_id(client, session, test_adventures, test_user, adventure_id, caption, image):
    jwt = {"Authorization" : f"bearer {test_user["jwt_token"]}"}
    data = {
        "adventure_id": adventure_id,
        "caption":  caption
    }
    files = {"image":  image}
    result = client.post("image/", data=data, files=files, headers=jwt)
    assert result.status_code == status.HTTP_200_OK
    image_query = session.query(models.Images).filter(models.Images.adventure_id == adventure_id).first()
    assert image_query.caption == caption


@pytest.mark.parametrize("adventure_id, caption, image, status_code", [
    (6, "nice view", ("image.jpg", b"file_content_1", "image/jpeg"), status.HTTP_404_NOT_FOUND),
    (1, "", ("image.jpg", b"", "image/jpeg"), status.HTTP_422_UNPROCESSABLE_ENTITY),
    (1, "nice view", ("image.png", b"file_content_1", "image/svg+xml"), status.HTTP_422_UNPROCESSABLE_ENTITY),
    (4, "nice view", ("image.webp", b"file_content_1", "image/webp"), status.HTTP_403_FORBIDDEN), #other users adventure
])
def test_invalid_post_image_id(client, session, test_adventures, test_user, adventure_id, caption, image, status_code):
    jwt = {"Authorization" : f"bearer {test_user["jwt_token"]}"}
    data = {
        "adventure_id": adventure_id,
        "caption":  caption
    }
    files = {"image":  image}
    result = client.post("image/", data=data, files=files, headers=jwt)
    assert result.status_code == status_code
    image_query = session.query(models.Images).filter(models.Images.adventure_id == adventure_id).first()
    assert not image_query

#----------------------------------[ TEST Put /image ]----------------------------------

def test_put_images(client, test_user, test_images, session, test_adventures):
    image_change = {
        "caption": "changed caption"
    }
    jwt = {"Authorization" : f"bearer {test_user["jwt_token"]}"}
    id = test_user["user_id"]
    result = client.put(f"image/{id}", json= image_change, headers=jwt)
    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()) == 2 
    image_query = session.query(models.Images).filter(models.Images.caption == "changed caption").first()
    assert image_query

def test_invalid_user_put_images(client, test_user, test_images, session, test_adventures):
    image_change = {
        "caption": "changed caption"
    }
    jwt = {"Authorization" : f"bearer {test_user["jwt_token"]}"}
    id = test_user["user_id"]
    result = client.put(f"image/3", json= image_change, headers=jwt)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

#----------------------------------[ TEST DELETE /image ]----------------------------------

def test_delete_image_success(client, test_user, test_images, session):
    image_id = test_images[0].image_id
    adventure_id = test_images[0].adventure_id
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}

    result = client.delete(f"/image/{image_id}", headers=jwt)
    assert result.status_code == status.HTTP_202_ACCEPTED
    assert all(image["adventure_id"] == adventure_id for image in result.json())

    deleted = session.query(models.Images).filter(models.Images.image_id == image_id).first()
    assert not deleted


@pytest.mark.parametrize("image_id, status_code", [
    (999, status.HTTP_404_NOT_FOUND),
    (0, status.HTTP_422_UNPROCESSABLE_ENTITY),
])
def test_delete_image_invalid(client, test_user, image_id, status_code):
    jwt = {"Authorization": f"bearer {test_user['jwt_token']}"}
    result = client.delete(f"/image/{image_id}", headers=jwt)
    assert result.status_code == status_code

def test_delete_image_unauthorized(client, test_user, test_images, test_adventures):
    user_id = 2
    wrong_user_jwt = create_access_token(data= {"user_id":2})
    jwt_header = {"Authorization": f"bearer {wrong_user_jwt}"}
    result = client.delete(f"/image/1", headers= jwt_header)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED

#----------------------------------[ TEST GET /image ]----------------------------------

def test_get_images_success(client, test_images):
    adventure_id = test_images[0].adventure_id
    result = client.get(f"/image/{adventure_id}")
    assert result.status_code == status.HTTP_200_OK
    assert all(image["adventure_id"] == adventure_id for image in result.json())


@pytest.mark.parametrize("adventure_id, status_code", [
    (0, status.HTTP_422_UNPROCESSABLE_ENTITY),
    (999, status.HTTP_404_NOT_FOUND),
])
def test_get_images_invalid(client, adventure_id, status_code):
    result = client.get(f"/image/{adventure_id}")
    assert result.status_code == status_code