from hub.tests import client, db


def test_email_send(client, db):
    
    from hub.models.membership import Person, Address
    from hub.services.email import send_email

    person = Person('good', 'email')
    db.session.add(person)

    addr = Address(person, 'EMAIL', 'PRIMARY', 'success@simulator.amazonses.com')
    db.session.add(addr)

    db.session.commit()

    r = send_email(
        person.primary_email,
        subject='This is a test email',
        body_html='<p>This is an email testing the email PeTU email system.</p>',
        body_text='This is an email testing the email PeTU email system.' 
    )

    assert r != False


def test_email_bounce(client, db):
    
    from hub.models.membership import Person, Address
    from hub.services.email import send_email

    person = Person('bad', 'email')
    db.session.add(person)

    addr = Address(person, 'EMAIL', 'PRIMARY', 'bounce@simulator.amazonses.com')
    db.session.add(addr)

    db.session.commit()

    r = send_email(
        person.primary_email,
        subject='This is a test email',
        body_html='<p>This is an email testing the email PeTU email system.</p>',
        body_text='This is an email testing the email PeTU email system.' 
    )

    assert r != False