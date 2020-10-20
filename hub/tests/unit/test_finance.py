"""
Tests for the Rate model
"""
from datetime import datetime, timedelta

from hub.tests import client


def test_get_amounts_return_correct_value(client):

    from hub.models.finance import Rate

    rate = Rate(10,datetime.today())

    rate.multiplier = 0.5
    rate.charge     = 1.25

    assert rate.net_amount == 6.25
    assert rate.amount           == 10


def test_active_returns_correct_value(client):
    
    from hub.models.finance import Rate

    past_date   = datetime.today() - timedelta(days=7)
    yesterday   = datetime.today() - timedelta(days=1)
    future_date = datetime.today() + timedelta(days=7)

    rate = Rate(10,past_date)
    rate.multiplier = 0.5
    rate.charge     = 1.25

    assert rate.ends_on   == None
    assert rate.is_active == True

    rate.ends_on = yesterday
    assert rate.is_active == False

    rate.ends_on = future_date
    assert rate.is_active == True


def test_bands_return_correct_amounts(client):

    from hub.models.finance import Band, Rate

