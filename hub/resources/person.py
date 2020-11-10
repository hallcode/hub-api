"""
APIs for registering and becoming a member.
"""

import datetime

from flask import Response, request, current_app
from flask_restful import Resource

from hub.exts import db
from hub.models.membership import Person


class PeopleApi(Resource):

    def post(self):
        """
        Create a new person.
        Only requires a name but can handle various other properties.
        """

        data = request.get_json()

        if data is None:
            return {}, 400

        if data["firstName"] is None or data["lastName"] is None:
            return {}, 400

        person = Person(data["firstName"], data["lastName"])
        
        if data["yearOfBirth"] is not None and data["monthOfBirth"] is not None and data["dayOfBirth"] is not None:
            person.date_of_birth = datetime.date(
                data["yearOfBirth"], 
                data["monthOfBirth"],
                data["dayOfBirth"]
            )

        db.session.add(person)
        db.session.commit()
        
        return person.__dict__, 201


class PersonApi(Resource):
    pass