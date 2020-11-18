from flask import Response, request, current_app
from flask_restful import Resource
from passlib.hash import argon2
from flask_jwt_extended import create_access_token

from hub.models.membership import Person


class LoginApi(Resource):
    
    def post(self):
        """
        Generate auth token for valid user
        """

        data = request.get_json()

        if "email" not in data:
            return {"errors": ["Please provide an email address."]}, 400

        if "password" not in data:
            return {"errors": ["Please provide your password."]}, 400

        person = Person.query.filter(Person.primary_email == data["email"]).first()

        if person is None:
            return {"errors": ["The username or password you provided was not recognised."]}, 400

        if not argon2.verify(data["password"], person.password):
            return {"errors": ["The username or password you provided was not recognised."]}, 400

        token = create_access_token(identity=person.id)

        return {"auth_token": token}, 200

        