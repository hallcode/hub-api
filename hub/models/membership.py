"""
Models for everything relating to people (users, members, etc)
"""
import datetime, hashlib
from string import ascii_uppercase
from passlib.hash import argon2

from hub.exts import db
from hub.services.time import months_to_days
from hub.services.geo import post_code_check
from hub.services.permissions import person_has, Gate
from hub.services.errors import InvalidValueError


class Person(db.Model):
    """
    A user who has subscribed to the mailing list
    """

    id = db.Column(db.String(10), primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime)
    ward_id = db.Column(db.String(10), nullable=True)
    district_id = db.Column(db.String(10), nullable=True)
    constituency_id = db.Column(db.String(10), nullable=True)
    landlord = db.Column(db.Boolean, nullable=True)
    own_house = db.Column(db.Boolean, nullable=True)
    pays_rent = db.Column(db.Boolean, nullable=True)
    restricted_job = db.Column(db.Boolean, nullable=True)

    stripe_customer_id = db.Column(db.String(255), nullable=True)
    stripe_payment_id = db.Column(db.String(255), nullable=True)

    password_hash = db.Column(db.String(300), nullable=True)

    addresses = db.relationship('Address', backref='person', lazy=False)
    phone_numbers = db.relationship('PhoneNumber', backref='person', lazy=True)
    email_addresses = db.relationship('EmailAddress', backref='person', lazy=False)
    email_sub = db.relationship('EmailSubscription', backref='person', lazy=False)
    roles = db.relationship('Role', backref='person', lazy=False)
    payments = db.relationship('Payment', backref='person', lazy=True)

    def __init__(self, first_name, last_name):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
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
        age = on.year - self.date_of_birth.year

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
        errors = ()
        if self.get_age() < 16:
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
    def password(self):
        raise Exception("Do not access password property directly.")

    @password.setter
    def password(self, password_raw):
        # @TODO Password verification required
        if password_raw is None:
            return
        self.password_hash = argon2.hash(password_raw)

    def check_password(self, password_raw):
        if password_raw is None or self.password_hash is None:
            return False
        return argon2.verify(password_raw, self.password_hash)

    def set_id(self):
        today = datetime.date.today()

        month = ascii_uppercase[today.month]
        count = Person.query.filter(
            Person.id.startswith('{:s}{:s}'.format(month, today.strftime('%y')))
        ).count()

        self.id = '{:s}{:s}{:02d}'.format(month, today.strftime('%y'), count + 1)
        checksum = str(self.calculate_id_checksum())
        self.id = '{:s}{:s}{:d}'.format(self.id, checksum, len(checksum))

    def calculate_id_checksum(self):
        checksum = 0
        for char in self.id:
            checksum = checksum + ord(char)

        checksum = checksum ** 2
        return checksum % 99

    @property
    def primary_email(self):
        for email in self.email_addresses:
            if email.type_code == 'PRIMARY':
                return email.email

    @primary_email.setter
    def primary_email(self, email):
        existing_email = EmailAddress.query.filter(EmailAddress.person_id == self.id).filter(
            EmailAddress.type_code == 'PRIMARY').first()
        if existing_email is None:
            new_email = EmailAddress(self, email, 'PRIMARY')
            db.session.add(new_email)

        else:
            if email != existing_email.email:
                existing_email.verified = False
            existing_email.email = email

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

    TYPES = (
        'HOME',
        'BILLING',
        'POSTAL',
        'TEMP',
    )

    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    type_code = db.Column(db.String(10), primary_key=True)
    line_1 = db.Column(db.String(1024))
    district = db.Column(db.String(1024))
    city = db.Column(db.String(1024))
    post_code = db.Column(db.String(13))

    def __init__(self, person, line_1, post_code, type):
        self.person = person
        self.line_1 = line_1
        self.post_code = post_code
        self.type = type

        codes = post_code_check(self.post_code)

        if codes is None:
            return

        self.person.ward_id = codes['admin_ward']
        self.person.district_id = codes['admin_district']
        self.person.constituency_id = codes['parliamentary_constituency']

    @property
    def type(self):
        return self.type_code.lower()

    @type.setter
    def type(self, code):
        if code not in self.TYPES:
            raise InvalidValueError('address.type', 'Invalid type code')

        self.type_code = code.upper()


class EmailAddress(db.Model):
    """
    Email Addresses
    """

    TYPES = (
        'PRIMARY',
        'BACKUP'
    )

    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    type_code = db.Column(db.String(10), primary_key=True)
    email = db.Column(db.String(1024), unique=True, nullable=False)
    verified = db.Column(db.Boolean, nullable=False, default=False)
    hard_bounce = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, person, email, type_code='PRIMARY'):
        self.person = person
        self.email = email
        self.type = type_code

        try:
            transactional_subscription = EmailSubscription(person, 'TRN')
            db.session.add(transactional_subscription)
        except:
            pass

    @property
    def type(self):
        return self.type_code.lower()

    @type.setter
    def type(self, code):
        if code not in self.TYPES:
            raise InvalidValueError('email.type', 'invalid type code')

        self.type_code = code.upper()

    def verify(self, code):
        test_token = self.email + str(code)
        test_token = hashlib.sha512(test_token.encode('UTF-8')).hexdigest()
        token = VerifyToken.query.get(test_token)

        if token is None:
            return False

        self.verified = True
        return True

    @property
    def is_active(self):
        return self.verified and not self.hard_bounce


class EmailSubscription(db.Model):
    """
    Record GDPR consent for each type of email we might send.
    Don't include transactional emails here, these will always be sent.
    """

    TYPES = (
        ("TRN", "Transactional",
         "Emails about your membership or user account. This could be a password reset email, or information about your monthly payments. We'lla lways send you these.",
         True),
        ("CWK", "Casework and advice", "If you ask us for advice or help on your case, we'll email you about that.",
         True),
        ("CON", "Constitutional", "Emails about elections and AGMs.", True),
        ("NAI", "Newsletters & Information",
         "Updates, information, and newsletters about the Union, its campaigns, and anything we think you might be interested in.",
         False),
        ("EVN", "Events",
         "Emails about protests, upcoming events, ordinary meetings and other things you can get involved in.", False),
    )

    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    type_code = db.Column(db.String(3), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now(), nullable=False)
    source = db.Column(db.String(30), nullable=False, default='online:join_form')
    text_shown = db.Column(db.Text, nullable=False)

    def __init__(self, person, type_code):
        self.person = person
        self.type = type_code
        self.created_at = datetime.datetime.now()

    class SubscriptionType:
        def __init__(self, code, types):
            for t in types:
                if code not in t:
                    continue

                self.code = t[0]
                self.title = t[1]
                self.description = t[2]
                self.required = t[3]
                return

            raise InvalidValueError('email_subscription.type', 'invalid type code')

    @property
    def type(self):
        return self.SubscriptionType(self.type_code.upper(), self.TYPES)

    @type.setter
    def type(self, code):
        code = self.SubscriptionType(code.upper(), self.TYPES)

        self.type_code = code.code
        self.text_shown = code.description


class PhoneNumber(db.Model):
    """
    Telephone numbers
    """

    TYPES = (
        "MOBILE",
        "HOME",
        "WORK",
    )

    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    type_code = db.Column(db.String(10), primary_key=True)
    number = db.Column(db.String(13), unique=True)
    sms = db.Column(db.Boolean, nullable=False)

    def __init__(self, person, number, type_code):
        self.person = person
        self.type = type_code
        self.number = number

    @property
    def type(self):
        return self.type_code.lower()

    @type.setter
    def type(self, code):
        if code not in self.TYPES:
            raise InvalidValueError('phone_number.type', 'invalid type code')

        self.type_code = code.upper()


class VerifyToken(db.Model):
    token = db.Column(db.String(300), primary_key=True)

    def __init__(self, user_id, code):
        raw_token = user_id + str(code)
        self.token = hashlib.sha512(raw_token.encode('UTF-8')).hexdigest()


class Role(db.Model):
    """
    Intermediate table between Person and RoleType
    """

    person_id = db.Column(db.String(10), db.ForeignKey('person.id'), primary_key=True)
    role_type_id = db.Column(db.Integer, db.ForeignKey('role_type.id'), primary_key=True)
    starts_on = db.Column(db.Date, nullable=False, primary_key=True)
    ends_on = db.Column(db.Date, nullable=True)

    def __init__(self, person, role_type, starts_on=datetime.date.today()):
        self.person = person
        self.type = role_type
        self.starts_on = starts_on

        if self.type.expires_after is not None:
            days = months_to_days(self.type.expires_after, starts_on)
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

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), unique=True, nullable=False)
    expires_after = db.Column(db.Integer, nullable=True)  # months
    auto_renews = db.Column(db.Boolean, default=False)
    available = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    joinable = db.Column(db.Boolean, nullable=False, default=False)
    elected = db.Column(db.Boolean, nullable=False, default=False)

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

    role_type_id = db.Column(db.Integer, db.ForeignKey('role_type.id'), primary_key=True)
    key = db.Column(db.String(50), primary_key=True)
    gate_func = db.Column(db.String(50), nullable=True)

    def __init__(self, role, key, must_be_active=False):
        self.role_type_id = role.id
        self.key = key

    def run_gate(self):
        if self.gate_func is None:
            return True

        person = self.role.person
        return Gate.run(self)
