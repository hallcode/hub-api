"""
APIs for registering and becoming a member.
"""

import datetime

from flask import Response, request, current_app, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, current_user
from passlib.hash import argon2

from hub.exts import db, jwt
from hub.models.membership import Person, Address
from hub.schemas.membership import PersonSchema
from hub.services.permissions import Gate
from hub.services.errors import UserNotAuthenticated, ActionNotAllowed, NotFoundError, InvalidValueError, EmptyBodyError


class PeopleApi(Resource):

    def post(self):
        """
        Create a new person.
        Only requires a name but can handle various other properties.
        """

        data = request.get_json()

        PersonSchema().load(data)

        if "firstName" not in data:
            raise InvalidValueError('firstName', 'field is blank')
        if "lastName" not in data:
            raise InvalidValueError('lastName', 'field is blank')

        person = Person(data["firstName"], data["lastName"])
        
        if "yearOfBirth" in data and "monthOfBirth" in data and "dayOfBirth" in data:
            try:
                person.date_of_birth = datetime.date(
                    int(data["yearOfBirth"]), 
                    int(data["monthOfBirth"]),
                    int(data["dayOfBirth"])
                )
            except:
                raise InvalidValueError('[x]ofBirth', 'date was not valid')

        db.session.add(person)
        db.session.commit()

        token = create_access_token(identity=person.id)
        
        return {
            "person": {
                "membership_number": person.id,
                "fullName": person.full_name
            },
            "auth_code": token
        }, 200


class PersonApi(Resource):
    
    def get(self, person_id):
        """
        Get a single person
        """

        person = Person.query.get(person_id)

        Gate.check('user_is_person', person=person)

        if person is None:
            raise NotFoundError(Person)

        return {"person":PersonSchema().dump(person)}

    def patch(self, person_id):
        """
        Update a person
        """

        person = Person.query.get(person_id)

        Gate.check('user_is_person', person=person)

        if person is None:
            raise NotFoundError(Person)

        data = request.get_json()

        for key, value in data.items():
            if key == "firstName":
                person.first_name = value
                continue
            
            if key == "lastName":
                person.last_name = value
                continue

            if key == "yearOfBirth":
                try:
                    person.date_of_birth = person.date_of_birth.replace(year=value)
                except:
                    raise InvalidValueError(key, 'date is invalid')
                continue

            if key == "monthOfBirth":
                if 1 > value < 12:
                    raise InvalidValueError(key, 'month must be between 1 and 12')
                    continue

                try:
                    person.date_of_birth = person.date_of_birth.replace(month=value)
                except:
                    raise InvalidValueError(key, 'date is invalid')
                continue

            if key == "dayOfBirth":
                try:
                    person.date_of_birth = person.date_of_birth.replace(day=value)
                except:
                    raise InvalidValueError(key, 'date is invalid')
                continue

            if key == "password":
                person.password = argon2.hash(value)
                continue

            if key == "paysRent":
                person.pays_rent = value
                continue

            if key == "ownHouse":
                person.own_house = value
                continue

            if key == "landlord":
                person.landlord = value
                continue

            if key == "restrictedJob":
                person.restricted_job = value
                continue

            if key == "primaryEmail":
                person.primary_email = value

            if key == "marketingConsent":
                email = Address.query.get((person.id, 'EMAIL', 'PRIMARY')).first()
                if email is None:
                    raise InvalidValueError(key, 'no valid email')

                email.marketing = True
                continue

            if key == "address":
                if not all (k in data["address"] for k in ("line_1", "district", "city", "postCode")):
                    raise InvalidValueError(key, 'please provide all address lines (i.e. "line_1", "district", "city", "postCode")')
                    continue

                address = person.get_address()

                if address is None:
                    address = Address(person, 'ADDR', 'HOME', value["line_1"])
                    db.session.add(address)
                else:
                    address.line_1 = value["line_1"]

                address.district  = value["district"]
                address.city      = value["city"]
                address.post_code = value["postCode"]

                person.set_locale()
                continue

        try:
            db.session.commit()
        except:
            raise Exception('There was a problem making the requested change')

        return {}, 204