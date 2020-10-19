
import os
import tempfile

import pytest
import hub


@pytest.fixture
def client():
    """Set up testing framework"""

    app = hub.create_app()

    # Basic config
    app.config.update(
        TESTING=True,
        SECRET_KEY=b'*T-E&S0T!I_N7G(',
        BCRYPT_LOG_ROUNDS=4,
        WTF_CSRF_ENABLED=False
    )

    with app.test_client() as client:
        yield client


@pytest.fixture(scope='module')
def init_database():
    # Create the database and the database table
    db.create_all()
 
    yield db  # this is where the testing happens!
 
    db.drop_all()