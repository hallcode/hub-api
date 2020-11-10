import stripe

from flask import current_app as app
from hub.exts import db
from hub.models.finance import Payment
from hub.models.membership import Person

stripe.api_key = app.config['STRIPE_SECRET']


def create_customer(person):
    """
    Generate a Stripe customer to use for reccuring payments.
    """

    if person.stripe_customer_id is not None:
        return stripe.Customer.retrieve(person.stripe_customer_id)
    
    customer = stripe.Customer.create(
        name=person.full_name,
        description=person.id,
        email=person.primary_email
    )

    person.stripe_customer_id = customer['id']
    db.session.commit()

    return customer


def generate_payment(person, amount):
    """
    Generates a payment intent with Stripe and a local payment object.
    This function is only to be used with on-session payments to be
    collected immediately after card capture.
    """
    
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='gbp',
        setup_future_usage='off_session',
        customer=person.stripe_customer_id
    )

    payment = Payment(
        person=person,
        amount=amount
    )
    payment.payment_intent_id = intent['id']

    db.session.add(payment)
    db.session.commit()

    return intent, payment


def capture_payment(payment):
    pass