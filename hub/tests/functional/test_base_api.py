from hub.tests import client, db


def test_root(client, db):
    """
    GIVEN the app is running
    WHEN GET '/'
    THEN 204 with no content
    """

    response = client.get('/')

    assert response.status_code == 204
    assert response.data == b''


def test_api_root(client, db):
    """
    GIVEN the app is running
    WHEN GET '/api'
    THEN 200 with basic info
    """

    response = client.get('/api')

    assert response.status_code == 200
    assert response.json == {
        "Api Name": "Hub - Peterborough Tenants' Union",
        "Version": 0.1
    }