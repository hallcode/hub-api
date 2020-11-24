import datetime
import random
from datetime import timedelta
from string import ascii_uppercase

from hub.tests import client, db


def test_person_returns_correct_names(client, db):

    from hub.models.membership import Person

    person = Person('billy', 'nomates')
    assert person.full_name == 'Billy Nomates'

    person.last_name = 'thefish'
    assert person.full_name == 'Billy Thefish'
    assert person.legal_name == 'THEFISH, Billy'


def test_person_id_returns_correctly(client, db):

    from hub.models.membership import Person

    today        = datetime.date.today()
    month_letter = ascii_uppercase[today.month]

    person = Person('billy', 'nomates')

    assert person.id[:3] == '{:s}{:s}'.format(month_letter, today.strftime('%y'))
    assert person.id[3:].isdigit()
    assert int(person.id[3:]) > 0


def test_age_returns_correctly(client, db):

    from hub.models.membership import Person

    person = Person('billy', 'nomates')

    person.date_of_birth = datetime.date(2010,1,1)
    comparison_date      = datetime.date(2020,1,1)
    assert person.get_age(on=comparison_date) == 10

    person.date_of_birth = datetime.date(2012,2,29)
    comparison_date      = datetime.date(2021,2,28)
    assert person.get_age(on=comparison_date) == 8

    comparison_date      = datetime.date(2021,3,1)
    assert person.get_age(on=comparison_date) == 9

    person.date_of_birth = datetime.date.today() - timedelta(weeks=950)
    assert person.get_age() == 18


def test_add_role_to_person(client, db):
    
    from hub.models.membership import Person, Role, RoleType

    person = Person('billy', 'nomates')
    person.date_of_birth = datetime.date(1990,10,11)
    db.session.add(person)

    role_type = RoleType("Role{:d}".format(random.randrange(0,99)), 1, True)
    db.session.add(role_type)

    role = Role(person, role_type, starts_on=datetime.date(2000,2,12))
    db.session.add(role)

    db.session.commit()

    assert role.person_id    == person.id
    assert role.ends_on      == datetime.date(2000,3,12)
    assert len(person.roles) == 1


def test_primary_email(client, db):

    from hub.models.membership import Person

    person = Person('billy', 'nomates')
    person.date_of_birth = datetime.date(1990,10,11)
    db.session.add(person)

    person.primary_email = "email@local.test"

    db.session.commit()

    assert person.primary_email == 'email@local.test'


def test_sms_number(client, db):

    from hub.models.membership import Person, PhoneNumber

    person = Person('billy', 'nomates')
    person.date_of_birth = datetime.date(1990,10,11)
    db.session.add(person)

    sms = PhoneNumber(person, '07712345690', 'MOBILE')
    sms.sms = True

    db.session.add(sms)
    db.session.commit()

    number_added = PhoneNumber.query.with_parent(person).filter(PhoneNumber.sms == True).first()

    assert number_added.number == '07712345690'


def test_get_address(client, db):

    from hub.models.membership import Person, Address

    person = Person('billy', 'nomates')
    person.date_of_birth = datetime.date(1990,10,11)
    db.session.add(person)

    addr1 = Address(person, '11 Anystreet', 'PE7 8JY', 'HOME')
    addr1.district  = 'District'
    addr1.city      = 'Anytown'
    db.session.add(addr1)

    db.session.commit()

    addr = person.addresses[0]

    assert len(person.addresses) == 1
    assert addr.line_1 == '11 Anystreet'
    assert addr.post_code == 'PE7 8JY'

    assert person.district_id == 'E06000031'
    assert person.constituency_id == 'E14000855'
    assert person.ward_id == 'E05010815'

    

