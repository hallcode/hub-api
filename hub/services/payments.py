import stripe

from flask import current_app as app
from hub.ext import db
from hub.models.finance import Payment

stripe.api_key = app.config['STRIPE_SECRET']


def generate_payment(person, amount):
    """
    Generates a payment intent with Stripe and a local payment object.
    This function is only to be used with on-session payments to be
    collected immediatley after card capture.
    """
    
    intent = stripe.PaymentIntent.create(
        amount=amount,
        currency='gbp',
        setup_future_usage=stripe.off_session
    )

    # Create payment
    payment = Payment(
        person=person,
        amound=amount
    )
    payment.payment_intent_id = intent['id']

    db.session.add(payment)
    db.session.commit()

    return intent, payment


def capture_payment(payment):
    pass