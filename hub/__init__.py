"""
Entry point for the Flask app
"""

from flask import Flask
import sys

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

from .config import Config
from hub.routes import load_routes

from .models import import_all_models


# Global Libraries
db = SQLAlchemy()
migrate = Migrate()
api = Api()


def create_app():
    """Create Flask app"""

    app = Flask(__name__)
    app.config.from_object(Config)

    init_db(app)

    load_routes(api)
    load_plugins(app)

    return app


def init_db(app):
    """Initialise database"""

    db.init_app(app)
    import_all_models()


def load_plugins(app):
    """Initialise global plugins"""

    migrate.init_app(app, db)
    api.init_app(app)