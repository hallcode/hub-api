from flask import Response, request
from flask_restful import Resource


class BaseApi(Resource):

    def get(self):
        return "Hello world!", 200