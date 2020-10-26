from hub.tests import client, db


def test_get_verify_code(client, db):

    from hub.models.membership import Person, Address

    EMAIL = 'alexhall93@me.com'

    person = Person('anne', 'Person')
    addr1 = Address(person, 'EMAIL', 'PRIMARY', EMAIL)
    db.session.add(person)
    db.session.add(addr1)

    db.session.commit()

    response = client.get('/api/verify/{:s}'.format(EMAIL))

    assert response.status_code == 200
    
    code = response.json["code"]
    assert code is not None

    