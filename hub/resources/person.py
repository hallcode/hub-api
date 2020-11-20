"""
APIs for registering and becoming a member.
"""

import datetime

from flask import Response, request, current_app
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

        schema = PersonSchema()

        json_data = request.get_json()
        data = schema.load(json_data)

        person = Person(data["first_name"], data["last_name"])
        db.session.add(person)

        for key, value in data.items():
            setattr(person, key, data[key])

        db.session.commit()

        token = create_access_token(identity=person.id)
        
        return {
            "person": schema.dump(person),
            "auth_code": token
        }


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

        schema = PersonSchema()
        person = Person.query.get(person_id)

        Gate.check('user_is_person', person=person)

        if person is None:
            raise NotFoundError(Person)

        json_data = request.get_json()
        data = schema.load(json_data)

        for key, value in data.items():
            setattr(person, key, data[key])

        try:
            db.session.commit()
        except:
            raise Exception('There was a problem making the requested change')

        return {"person":schema.dump(person)}