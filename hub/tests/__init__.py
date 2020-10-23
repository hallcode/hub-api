
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
        WTF_CSRF_ENABLED=False
    )

    with app.test_client() as client:
        with app.app_context():
            yield client

    hub.api = Api()