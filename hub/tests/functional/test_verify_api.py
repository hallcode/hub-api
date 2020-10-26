import urllib.parse, json
from hub.tests import client, db


def test_get_verify_code(client, db):

    from hub.models.membership import Person, Address

    EMAIL = 'success@simulator.amazonses.com'

    person = Person('anne', 'Person')
    addr1 = Address(person, 'EMAIL', 'PRIMARY', EMAIL)
    db.session.add(person)
    db.session.add(addr1)

    db.session.commit()

    email_addr = urllib.parse.quote(EMAIL)
    response = client.get('/api/verify/{:s}'.format(email_addr))

    assert response.status_code == 200
    
    code = response.json["code"]
    assert code is not None

    response = client.post(
        '/api/verify/{:s}'.format(email_addr), 
        data=json.dumps({
            'code': 'abc123'
        }), 
        content_type='application/json'
    )

    assert response.status_code == 400

    db.session.refresh(addr1)
    assert addr1.verified == False

    response = client.post(
        '/api/verify/{:s}'.format(email_addr), 
        data=json.dumps({
            'code': code
        }), 
        content_type='application/json'
    )

    assert response.status_code == 204

    db.session.refresh(addr1)
    assert addr1.verified == True