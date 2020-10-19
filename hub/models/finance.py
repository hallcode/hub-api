"""
Models for payments etc
"""

from datetime import datetime
from hub import db


class Band(db.Model):
    """An adjustment to a Rate"""

    id          = db.Column(db.Integer, primary_key=True)
    code        = db.Column(db.String(3))
    name        = db.Column(db.String(15))
    description = db.Column(db.Text, nullable=True)
    multiplier  = db.Column(db.Numeric(4,3))
    starts_on   = db.Column(db.Date)
    ends_on     = db.Column(db.Date)


    def is_active(self):
        return (self.starts_on < datetime.today()) and (self.ends_on > datetime.today())


class Rate(db.Model):
    """Base membership rates from which bands are calculated"""

    id         = db.Column(db.Integer, primary_key=True)
    starts_on  = db.Column(db.Date)
    ends_on    = db.Column(db.Date)
    amount     = db.Column(db.Numeric(5,3))
    multiplier = db.Column(db.Numeric(4,3))
    charge     = db.Column(db.Numeric(5,3))


    def get_net_amount(self):
        return (self.amount * self.multiplier) + self.charge

    def is_active(self):
        return (self.starts_on < datetime.today()) and (self.ends_on > datetime.today())