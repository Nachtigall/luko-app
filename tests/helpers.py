import json
import os
import tempfile
from unittest import mock

import pytest

from app import app, db
from app.config import TestingConfig
from app.external.la_poste import LaPosteAPI


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp()
    app.config.from_object(TestingConfig)
    app.config.update({"SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}"})

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

    os.close(db_fd)
    os.unlink(db_path)


def json_of_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode())


@pytest.fixture()
def mock_la_poste():
    with mock.patch("app.views.api_endpoints.la_poste_api") as mock_la_poste:
        mock_la_poste.get_letter_details.return_value = "testing status"
        yield mock_la_poste


@pytest.fixture()
def la_poste_api():
    la_poste_api = LaPosteAPI(app.config["LA_POST_API_ENDPOINT"], app.config["LA_POST_API_KEY"],
                              app.config["LA_POST_API_LANGUAGE"])
    yield la_poste_api


@pytest.fixture()
def mock_requests():
    with mock.patch("app.external.la_poste.requests.get") as mock_req:
        yield mock_req
