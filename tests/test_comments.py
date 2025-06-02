"""
test_comments.py

=+=+=+=+=+=+=+=+=+=+=+=+=+=+=[ Tests for comments Endpoints ]=+=+=+=+=+=+=+=+=+=+=+=+=+=+=

"""
from fastapi import status

from tests.conftest import test_user, test_adventures, session, client
from app.oauth2 import create_access_token
from app.models import Comments
#----------------------------------[ TEST POST /adventure/{adventure_id}/comment ]----------------------------------

def test_post_comment(client, session, test_user, test_adventures):
    comment_str = "sample comment"
    jwt = {"Authorization" : f"bearer {test_user['jwt_token']}"}
    data = {
        'comment': f"{comment_str}"
    }
    result = client.post('/adventure/1/comments', json=data, headers =jwt)
    assert result.status_code == status.HTTP_201_CREATED
    comment_query = session.query(Comments).filter(Comments.comment == comment_str)
    assert comment_query

def test_invalid_adventure_id_post_comment(client, session,test_user, test_adventures):
    jwt = {"Authorization" : f"bearer {test_user['jwt_token']}"}
    data = {
        'comment': "sample comment"
    }
    result = client.post('/adventure/5/comments', json=data, headers =jwt)
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert result.json().get('detail') == "could not find adventure with adventure id = 5"

#----------------------------------[ TEST GET /adventure/{adventure_id}/comment ]----------------------------------
def test_get_adventure_comments(client, session, test_adventures, test_comments):
    result = client.get("/adventure/1/comments")
    assert result.status_code == status.HTTP_200_OK
    assert len(result.json()) == 3

def test_invalid_get_adventure_comments(client, session, test_comments):
    result = client.get("/adventure/7/comments")
    assert result.status_code == status.HTTP_404_NOT_FOUND
    assert result.json().get('detail') == "could not find adventure with adventure id = 7"

#----------------------------------[ TEST DELETE /adventure/comment/{comment_id} ]----------------------------------
def test_delete_comment(client, session, test_adventures, test_comments, test_user):
    jwt = {"Authorization" : f"bearer {test_user['jwt_token']}"}
    result = client.delete("/adventure/comment/1", headers = jwt)
    assert result.status_code == status.HTTP_204_NO_CONTENT
    comment_query = session.query(Comments).filter(Comments.comment_id == 1).first()
    assert not comment_query

def test_invalid_user_delete_comment(client, session, test_adventures, test_comments, test_user):
    user_id = 2
    wrong_user_jwt = create_access_token(data= {"user_id":2})

    jwt = {"Authorization" : f"bearer {wrong_user_jwt}"}
    result = client.delete("/adventure/comment/1", headers = jwt)
    assert result.status_code == status.HTTP_401_UNAUTHORIZED
    assert result.json().get('detail') == 'You are not permitted to delete comments from this adventure'


#----------------------------------[ TEST PUT /adventure/comment/{comment_id} ]----------------------------------

#Currently the program does not call for updating comments