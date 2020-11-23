from hub.tests import client, db


def test_email_send(client, db):
    
    from hub.models.membership import Person
    from hub.models.messaging import Email
    from hub.services.email import send_email

    person = Person('anne', 'Person')
    person.primary_address = 'success@simulator.amazonses.com'
    
    db.session.add(person)
    db.session.commit()

    email = Email(
        sender=person,
        subject='Test Message',
        body=f"""Dear {{{{ to.first_name }}}} {{{{ to.last_name }}}},

## This is a test message

I hope you got this! It's a test :)"""
    )

    email.type_code = "TRN"

    assert email.status == 'CREATED'

    email.to_all_members = True

    db.session.add(email)
    db.session.commit()

    email.send()

    assert email.status == 'SENT'


def test_email_bounce(client, db):
    
    from hub.models.membership import Person
    from hub.services.email import send_email

    person = Person('bad', 'email')
    person.primary_email = 'bounce@simulator.amazonses.com'

    db.session.add(person)
    db.session.commit()

    r = send_email(
        person.primary_email,
        subject='This is a test email',
        body_html='<p>This is an email testing the email PeTU email system.</p>',
        body_text='This is an email testing the email PeTU email system.' 
    )

    assert r != False