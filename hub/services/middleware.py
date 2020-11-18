"""
Anything that is run before or after the flask request
"""

from flask import g, current_app, request
from flask_jwt_extended import verify_jwt_in_request_optional
from werkzeug.exceptions import HTTPException

from hub.exts import jwt
from hub.models.membership import Person
from hub.services.errors import Error, TokenError


@jwt.user_loader_callback_loader
def user_loader(identity):
    return Person.query.get(identity)


@current_app.before_request
def get_user_from_token():
    try:
        verify_jwt_in_request_optional()
    except:
        raise TokenError