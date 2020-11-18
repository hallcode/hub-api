"""
Entry point for the Flask app
"""

# Framework import
from flask import Flask

# App imports
from .config import Config
from hub.routes import load_routes
from .models import import_all_models
from .exts import db, migrate, api, jwt


def create_app():
    """Create Flask app"""

    app = Flask(__name__)
    app.config.from_object(Config)

    with app.app_context():
        init_db(app)

        load_routes(api)
        create_app.resources_added = True

        load_plugins(app)

        import hub.services.middleware

        handle_errors(app)

    return app


def init_db(app):
    """Initialise database"""

    db.init_app(app)
    import_all_models()


def load_plugins(app):
    """Initialise global plugins"""

    migrate.init_app(app, db)
    api.init_app(app)
    jwt.init_app(app)


def handle_errors(app):
    """
    Properly handle errors
    """

    from hub.services.errors import Error

    def handle_generic_error(e):
        return {"error": str(e)}, e.code

    app.register_error_handler(Error, handle_generic_error)