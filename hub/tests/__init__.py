
import os
import tempfile

import pytest
import hub
from hub.exts import db as database

from flask_restful import Api


@pytest.fixture
def client():
    """Set up testing framework"""

    app = hub.create_app()

    # Basic config
    app.config.update(
        TESTING=True,
        SECRET_KEY=b'*T-E&S0T!I_N7G(',
        BCRYPT_LOG_ROUNDS=4,
        WTF_CSRF_ENABLED=False,
        SQLALCHEMY_DATABASE_URI='sqlite:///test.db',
        STRIPE_SECRET=os.environ.get('STRIPE_TEST_SECRET'),
        STRIPE_PUBLIC=os.environ.get('STRIPE_TEST_PUBLIC')
    )

    with app.test_client() as client:
        with app.app_context():
            yield client

    hub.api = Api()


@pytest.fixture
def db():
    """Init test database"""

    database.create_all()

    yield database

    database.drop_all()