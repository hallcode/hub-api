"""
Models for everything relating to people (users, members, etc)
"""
import datetime, calendar
from math import floor
from string import ascii_uppercase

from hub import db
from hub.services.time import months_to_days


class Person(db.Model):
    """
    A user who has subscribed to the mailing list
    """

    id            = db.Column(db.String(10), primary_key=True)
    first_name    = db.Column(db.String(255), nullable=False)
    last_name     = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    created_at    = db.Column(db.DateTime)

    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_payment_id  = db.Column(db.String(255), nullable=True)

    addresses = db.relationship('Address', backref='person', lazy=False)
    roles     = db.relationship('Role', backref='person', lazy=False)
    payments  = db.relationship('Payment', backref='person', lazy=True)

    def __init__(self, first_name, last_name):
        self.first_name = first_name.title()
        self.last_name  = last_name.title()
        self.created_at = datetime.datetime.now()
        
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


class Address(db.Model):
    """
    Addresses
    """
    
    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    type      = db.Column(db.String(10), primary_key=True)
    usage     = db.Column(db.String(10), nullable=False)
    verified  = db.Column(db.Boolean, nullable=False, default=False)
    line_1    = db.Column(db.String(1024))
    district  = db.Column(db.String(1024))
    city      = db.Column(db.String(1024))
    post_code = db.Column(db.String(10))

    
class RoleType(db.Model):
    """
    Types of roles available for people to have
    """

    id            = db.Column(db.Integer, primary_key=True)
    title         = db.Column(db.String(255), unique=True, nullable=False)
    expires_after = db.Column(db.Integer, nullable=True) # months
    auto_renews   = db.Column(db.Boolean, default=False)
    available     = db.Column(db.Boolean, default=True)
    category      = db.Column(db.String(255), nullable=True)
    description   = db.Column(db.Text, nullable=True)
    joinable      = db.Column(db.Boolean, nullable=False, default=False)
    elected       = db.Column(db.Boolean, nullable=False, default=False)

    rates = db.relationship('Rate', backref='role_type', lazy=False)
    roles = db.relationship('Role', backref='type', lazy=False)

    def __init__(self, title, expires_after=None, auto_renews=False):
        self.title = title.title()

        if expires_after is not None:
            self.expires_after = expires_after

        if auto_renews:
            self.auto_renews = True

    @property
    def chargable(self):
        if self.rates is None:
            return False

        return True


class Role(db.Model):
    """
    Intermediate table between Person and RoleType
    """

    person_id    = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    role_type_id = db.Column(db.Integer, db.ForeignKey('role_type.id'), primary_key=True)
    starts_on    = db.Column(db.Date, nullable=False, primary_key=True)
    ends_on      = db.Column(db.Date, nullable=True)

    def __init__(self, person, role_type, starts_on=datetime.date.today()):
        self.person    = person
        self.type      = role_type
        self.starts_on = starts_on

        if self.type.expires_after is not None:
            days         = months_to_days(self.type.expires_after, starts_on)
            self.ends_on = starts_on + datetime.timedelta(days=days)
