from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow


# Create global Libraries
db = SQLAlchemy()
migrate = Migrate()
api = Api()
jwt = JWTManager()
ma = Marshmallow()