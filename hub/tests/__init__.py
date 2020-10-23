
import os
import tempfile

import pytest
import hub

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
        SQLALCHEMY_DATABASE_URI='sqlite:///test.db'
    )

    with app.test_client() as client:
        with app.app_context():
            yield client

    hub.api = Api()


@pytest.fixture
def db():
    """Init test database"""

    db = hub.db
    db.create_all()

    yield db

    db.drop_all()