from flask import Response, request, current_app
from flask_restful import Resource


class RootApi(Resource):
    def get(self):
        """
        Handle requests to '/'.
        These shouldn't ever be made as the server should be configured to direct 
        this endpoint to the front-end.
        """
        return "", 204


class BaseApi(Resource):

    def get(self):
        """Handle requests to the API root endpoint."""
        return {
            "Api Name": "Hub - Peterborough Tenants' Union",
            "Version": 0.1,
            "db_con_string": current_app.config['SQLALCHEMY_DATABASE_URI']
        }, 200