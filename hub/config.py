"""
Flask config.

Run the following before starting the app for the first time:
$ cp example.env .env

Then change the values in .env to the ones required for your environment
"""

from os import environ, path

basedir = path.abspath(path.dirname(__file__))


class Config:
    """Flask Specific config variables"""

    # Do not set FLASK_ENV here! It will have no effect.
    SECRET_KEY = environ.get('SECRET_KEY')
    PROPAGATE_EXCEPTIONS = environ.get('PROPAGATE_EXCEPTIONS', True)

    # Database
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS', False)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = environ.get('SQLALCHEMY_COMMIT_ON_TEARDOWN', False)
    DATABASE_CONNECT_OPTIONS = {}

    # Email
    GLOBAL_FROM_ADDR = environ.get('GLOBAL_FROM_ADDR', 'dev@localhost.test')
    TEMPLATE_PATH = environ.get('TEMPLATE_PATH', 'hub/templates')

    # Stripe
    STRIPE_SECRET = environ.get('STRIPE_SECRET')
    STRIPE_PUBLIC = environ.get('STRIPE_PUBLIC')
