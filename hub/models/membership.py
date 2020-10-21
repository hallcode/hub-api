"""
Models for everything relating to people (users, members, etc)
"""
from math import floor
import datetime
from string import ascii_uppercase

from hub import db


class Person(db.Model):
    """
    A user who has subscribed to the mailing list
    """

    id            = db.Column(db.String(10), primary_key=True)
    first_name    = db.Column(db.String(255), nullable=False)
    last_name     = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)


    def __init__(self, first_name, last_name):
        self.first_name = first_name.title()
        self.last_name  = last_name.title()

        self.set_id()

    def __repr__(self):
        return '<Person [{:s}]>'.format(self.id)

    @property
    def full_name(self):
        return '{:s} {:s}'.format(self.first_name.title(), self.last_name.title())

    def get_age(self, on=datetime.date.today()):
        age  = on.year  - self.date_of_birth.year

        if on.month > self.date_of_birth.month:
            return age

        if on.month < self.date_of_birth.month:
            return age - 1

        # If we're here, it means their birthday is this month
        if on.day >= self.date_of_birth.day:
            return age
        else:
            return age - 1

    def set_id(self):
        today = datetime.date.today()

        month = ascii_uppercase[today.month]
        count = Person.query.filter(
            Person.id.startswith('{:s}{:s}'.format(month, today.strftime('%y')))
        ).count()

        self.id = '{:s}{:s}{:03d}'.format(month, today.strftime('%y'), count+1)


    
class RoleType(db.Model):
    """
    Types of roles available for people to have
    """

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(255), unique=True, nullable=False)
    expires_after = db.Column(db.Integer, nullable=True) # Months
    auto_renews   = db.Column(db.Boolean, default=False)
    available     = db.Column(db.Boolean, default=True)
    category      = db.Column(db.String(255), nullable=True)
    description   = db.Column(db.Text, nullable=True)
    joinable      = db.Column(db.Boolean, nullable=False, default=False)

    rates = db.relationship('Rate', backref='role_type', lazy=True)


    def __init__(self, title, expires_after=None, lapse_after=None, auto_renews=False):
        self.title = title.title()

        if expires_after is not None:
            self.expires_after = expires_after

        if lapse_after is not None:
            self.lapse_after = lapse_after

        if auto_renews:
            self.auto_renews = True

    @property
    def chargable(self):
        if self.rates is None:
            return False

        return True


class Role(db.Model):
    """
    Roles people actually hold
    """

    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    role_id   = db.Column(db.Integer, db.ForeignKey('role_type.id'), primary_key=True)
    starts_on = db.Column(db.Date, nullable=False, primary_key=True)
    ends_on   = db.Column(db.Date, nullable=True)
    
    type = db.relationship('RoleType', backref='role', lazy=True)