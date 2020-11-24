from hub.tests import client, db
from flask_jwt_extended import create_access_token


def test_get_person_returns_okay(client, db):
    """
    GIVEN a valid person
    WHEN GET '/api/people/<id>'
    THEN returns person object 200 response
    """

    from hub.models.membership import Person

    # Add person
    FIRST_NAME = "Test"
    LAST_NAME  = "Person"
    person = Person(FIRST_NAME, LAST_NAME)

    db.session.add(person)
    db.session.commit()

    token = create_access_token(identity=person.id)

    # With Correct Header
    r = client.get(f'/api/people/{person.id}', headers={"Authorization": f'Bearer {token}'})

    assert r.status_code == 200
    assert "person" in r.json
    assert "id" in r.json["person"]
    assert "full_name" in r.json["person"]
    assert r.json["person"]["full_name"] == f'{FIRST_NAME.title()} {LAST_NAME.title()}'
    assert r.json["person"]["id"] == person.id

    # With header of a different user
    user = Person(FIRST_NAME, LAST_NAME)
    db.session.add(user)
    db.session.commit()

    user_token = create_access_token(identity=user.id)

    rb = client.get(f'/api/people/{person.id}', headers={"Authorization": f'Bearer {user_token}'})

    assert rb.status_code == 403
    assert "person" not in rb.json


def test_get_person_logged_out_not_allowed(client, db):

    from hub.models.membership import Person

    # Add person
    FIRST_NAME = "Test"
    LAST_NAME  = "Person"
    person = Person(FIRST_NAME, LAST_NAME)
    db.session.add(person)
    
    db.session.commit()

    # With no header
    r2 = client.get(f'/api/people/{person.id}')
    assert r2.status_code == 401
    assert "person" not in r2.json
