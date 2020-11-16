from flask import Response, request, current_app
from flask_restful import Resource


class LoginApi(Resource):
    
    def post(self):
        """
        Generate auth token for valid user
        """