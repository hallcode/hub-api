"""
Models for everything relating to people (users, members, etc)
"""
import datetime, calendar, hashlib
from math import floor
from string import ascii_uppercase

from hub.exts import db
from hub.services.time import months_to_days
from hub.services.geo import post_code_check
from hub.services.permissions import person_has, Gates


class Person(db.Model):
    """
    A user who has subscribed to the mailing list
    """

    id              = db.Column(db.String(10), primary_key=True)
    first_name      = db.Column(db.String(255), nullable=False)
    last_name       = db.Column(db.String(255), nullable=False)
    date_of_birth   = db.Column(db.Date, nullable=True)
    created_at      = db.Column(db.DateTime)
    ward_id         = db.Column(db.String(10), nullable=True)
    district_id     = db.Column(db.String(10), nullable=True)
    constituency_id = db.Column(db.String(10), nullable=True)
    landlord        = db.Column(db.Boolean, nullable=True)
    own_house       = db.Column(db.Boolean, nullable=True)
    pays_rent       = db.Column(db.Boolean, nullable=True)
    restricted_job  = db.Column(db.Boolean, nullable=True)

    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_payment_id  = db.Column(db.String(255), nullable=True)

    password = db.Column(db.String(300), nullable=True)

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

    @property
    def legal_name(self):
        return '{:s}, {:s}'.format(self.last_name.upper(), self.first_name)

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

    @property
    def is_eligable(self):
        eligable = True
        errors   = ()
        if self.age < 16:
            eligable = False
            errors = errors + ('Members must be over the age of 16.',)
        
        if self.landlord:
            eligable = False
            errors = errors + ('Members cannot be landlords.',)

        if self.own_house:
            eligable = False
            errors = errors + ('Members must live in a house they do not own.',)

        if self.restricted_job:
            eligable = False
            errors = errors + ('Members must not work with evictions.',)

        if not self.pays_rent:
            eligable = False
            errors = errors + ('Members must pay some sort of rent for their house.',)

        return eligable, errors

    @property
    def primary_email(self):
        return Address.query.get((self.id, 'EMAIL', 'PRIMARY')).line_1

    @property
    def sms_number(self):
        return Address.query.get((self.id, 'TEL', 'SMS')).line_1

    def get_address(self, type='HOME'):
        return Address.query.get((self.id, 'ADDR', type))

    def set_locale(self):
        addr = self.get_address()
        if addr is None:
            return 

        codes = post_code_check(addr.post_code)

        if codes is None:
            return

        self.ward_id         = codes['admin_ward']
        self.district_id     = codes['admin_district']
        self.constituency_id = codes['parliamentary_constituency']

    def set_id(self):
        today = datetime.date.today()

        month = ascii_uppercase[today.month]
        count = Person.query.filter(
            Person.id.startswith('{:s}{:s}'.format(month, today.strftime('%y')))
        ).count()

        self.id = '{:s}{:s}{:03d}'.format(month, today.strftime('%y'), count+1)

    def has(self, abilities=None, roles=None):
        from functools import wraps
        def outer_wrapper(f):
            @wraps(f)
            def inner_wrapper(*args, **kwargs):
                if person_has(self, abilities, roles):
                    return f(*args, **kwargs)
                else:
                    return {}, 403
            return inner_wrapper
        return outer_wrapper


class Address(db.Model):
    """
    Addresses
    """

    TYPES = {
        "ADDR": ('HOME','BILLING','POST'),
        "EMAIL": ('PRIMARY','BACKUP'),
        "TEL": ('SMS','LANDLINE')
    }
    
    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    type      = db.Column(db.String(10), primary_key=True)
    usage     = db.Column(db.String(10), primary_key=True)
    verified  = db.Column(db.Boolean, nullable=False, default=False)
    line_1    = db.Column(db.String(1024))
    district  = db.Column(db.String(1024))
    city      = db.Column(db.String(1024))
    post_code = db.Column(db.String(10))
    marketing = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, person, type, usage, line_1):
        if type not in self.TYPES:
            raise Exception
        self.type = type
        if usage not in self.TYPES[type]:
            raise Exception
        self.usage = usage

        self.person = person
        self.line_1 = line_1
        

class VerifyToken(db.Model):
    token = db.Column(db.String(300), primary_key=True)

    def __init__(self, user_id, code):
        raw_token = user_id+str(code)
        self.token = hashlib.sha512(raw_token.encode('UTF-8')).hexdigest()


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

    def is_active(self):
        return self.starts_on < datetime.date() < self.ends_on


    @property
    def abilities(self):
        return self.type.abilities


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


class Ability(db.Model):
    """
    Represents a permission that a role has
    """

    role_type_id   = db.Column(db.Integer, db.ForeignKey('role_type.id'), primary_key=True)
    key            = db.Column(db.String(50), primary_key=True)
    gate_func      = db.Column(db.String(50), nullable=True)

    def __init__(self, role, key, must_be_active=False):
        self.role_type_id   = role.id
        self.key            = key

    def run_gate(self):
        if self.gate_func is None:
            return True

        person = self.role.person
        return Gates.run(self)