import os
import tempfile

os.environ["DATABASE_URL"] = f"sqlite:///{tempfile.mkdtemp(prefix='thrive-tests-')}/test.db"

import pytest
from fastapi.testclient import TestClient

from thrive.database import Base, engine
from thrive.main import app


@pytest.fixture
def client() -> TestClient:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with TestClient(app) as test_client:
        yield test_client
