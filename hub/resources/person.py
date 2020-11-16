"""
APIs for registering and becoming a member.
"""

import datetime

from flask import Response, request, current_app, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token

from hub.exts import db, jwt
from hub.models.membership import Person


class PeopleApi(Resource):

    def post(self):
        """
        Create a new person.
        Only requires a name but can handle various other properties.
        """

        data = request.get_json()

        if data is None:
            return {
                "error": "The request was empty."
            }, 400

        if "firstName" not in data or "lastName" not in data:
            return {
                "error": "Missing required fields: firstName or lastName were blank."
            }, 400

        person = Person(data["firstName"], data["lastName"])
        
        if "yearOfBirth" in data and "monthOfBirth" in data and "dayOfBirth" in data:
            try:
                person.date_of_birth = datetime.date(
                    int(data["yearOfBirth"]), 
                    int(data["monthOfBirth"]),
                    int(data["dayOfBirth"])
                )
            except:
                return {
                    "error": "The date of birth you provided was not valid."
                }, 400

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
    pass