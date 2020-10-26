"""
Models for payments etc
"""

from datetime import datetime
from hub.exts import db


class Band(db.Model):
    """An adjustment to a Rate"""

    id          = db.Column(db.Integer, primary_key=True)
    code        = db.Column(db.String(3))
    name        = db.Column(db.String(15))
    description = db.Column(db.Text, nullable=True)
    multiplier  = db.Column(db.Numeric(4,3))
    starts_on   = db.Column(db.Date)
    ends_on     = db.Column(db.Date)
    rate_id     = db.Column(db.Integer, db.ForeignKey('rate.id'), nullable=False)

    def __init__(self, code, rate):
        self.code    = str(code).upper()
        self.rate    = rate

    @property
    def is_active(self):
        if (self.starts_on < datetime.today()) and (self.ends_on is None):
            return True

        if (self.starts_on < datetime.today()) and (self.ends_on > datetime.today()):
            return True

        return False

    @property
    def net_amount(self):
        return ( (self.rate.amount * self.multiplier) * self.rate.multiplier ) + self.rate.charge


class Rate(db.Model):
    """Base membership rates from which bands are calculated"""

    id           = db.Column(db.Integer, primary_key=True)
    starts_on    = db.Column(db.Date, nullable=False)
    ends_on      = db.Column(db.Date)
    amount       = db.Column(db.Numeric(5,3), nullable=False)
    multiplier   = db.Column(db.Numeric(4,3), nullable=False, default=0)
    charge       = db.Column(db.Numeric(5,3), nullable=False, default=0)
    role_type_id = db.Column(db.Integer, db.ForeignKey('role_type.id'), nullable=False)

    bands = db.relationship(Band, backref='rate', lazy=True)

    def __init__(self, amount, starts_on):
        self.amount    = amount
        self.starts_on = starts_on

    @property
    def net_amount(self):
        return (self.amount * self.multiplier) + self.charge

    @property
    def is_active(self):
        if (self.starts_on < datetime.today()) and (self.ends_on is None):
            return True

        if (self.starts_on < datetime.today()) and (self.ends_on > datetime.today()):
            return True

        return False


class Payment(db.Model):
    """
    Log table for all payments collected
    """

    id        = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), nullable=False)
    amount    = db.Column(db.Numeric(5,3), nullable=False, default=0)
    status    = db.Column(db.String(7), nullable=False, default='CREATED')

    def __init__(self, person, amount):
        self.timestamp = datetime.now()
        self.person    = person
        self.amount    = amount

    def collect(self):
        self.timestamp = datetime.now()
