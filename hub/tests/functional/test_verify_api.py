import urllib.parse, json
from hub.tests import client, db


def test_get_verify_code(client, db):

    from hub.models.membership import Person, EmailAddress

    EMAIL = 'success@simulator.amazonses.com'

    person = Person('anne', 'Person')
    person.primary_email = EMAIL
    
    db.session.add(person)
    db.session.commit()

    email_addr = urllib.parse.quote(EMAIL)
    response = client.get('/api/verify/{:s}'.format(email_addr))

    assert response.status_code == 204

    response = client.post(
        '/api/verify/{:s}'.format(email_addr), 
        data=json.dumps({
            'code': 'abc123'
        }), 
        content_type='application/json'
    )

    assert response.status_code == 400