import datetime
import random
from datetime import timedelta
from string import ascii_uppercase

from hub import db
from hub.tests import client


def test_person_returns_correct_names(client):

    from hub.models.membership import Person

    person = Person('billy', 'nomates')
    assert person.full_name == 'Billy Nomates'

    person.last_name = 'thefish'
    assert person.full_name == 'Billy Thefish'


def test_person_id_returns_correctly(client):

    from hub.models.membership import Person

    today        = datetime.date.today()
    month_letter = ascii_uppercase[today.month]

    person = Person('billy', 'nomates')

    assert person.id[:3] == '{:s}{:s}'.format(month_letter, today.strftime('%y'))
    assert person.id[3:].isdigit()
    assert int(person.id[3:]) > 0


def test_age_returns_correctly(client):

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


def test_add_role_to_person(client):
    
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