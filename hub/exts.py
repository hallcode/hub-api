from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

# Create global Libraries
db = SQLAlchemy()
migrate = Migrate()
api = Api()