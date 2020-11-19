from flask import Response, request, current_app
from flask_restful import Resource
from passlib.hash import argon2
from flask_jwt_extended import create_access_token

from hub.models.membership import Person, Address
from hub.services.errors import InvalidValueError


class LoginApi(Resource):
    
    def post(self):
        """
        Generate auth token for valid user
        """

        data = request.get_json()

        if "email" not in data:
            raise InvalidValueError("email", "field is blank")

        if "password" not in data:
            raise InvalidValueError("password", "field is blank")

        person = None
        addr = Address.query.filter(Address.line_1 == data["email"]).first()

        if addr is not None:
            person = addr.person

        if person is None:
            raise InvalidValueError("email", "user not found")

        if not argon2.verify(data["password"], person.password):
            raise InvalidValueError("email", "user not found")

        token = create_access_token(identity=person.id)

        return {"auth_token": token}, 200

        