from hub.tests import client, db

def test_create_customer_service(client, db):

    from hub.models.membership import Person, Address
    from hub.services.payments import create_customer

    person = Person('anne', 'Person')
    addr = Address(person, 'EMAIL', 'PRIMARY', 'success@simulator.amazonses.com')
    db.session.add(person)
    db.session.add(addr)

    db.session.commit()

    customer = create_customer(person)

    assert person.stripe_customer_id is not None
    assert person.stripe_customer_id == customer['id']


def test_create_payment_intent_service(client, db):

    from hub.models.membership import Person, Address
    from hub.models.finance import Payment
    from hub.services.payments import create_customer, generate_payment

    person = Person('anneother', 'Person')
    addr = Address(person, 'EMAIL', 'PRIMARY', 'success@simulator.amazonses.com')
    db.session.add(person)
    db.session.add(addr)

    db.session.commit()

    customer        = create_customer(person)
    intent, payment = generate_payment(person, 500)

    assert person.stripe_customer_id is not None
    assert Payment.query.with_parent(person).count() > 0
    assert payment.payment_intent_id == intent['id']


