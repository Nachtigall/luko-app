import pytest
import requests

from app.external.la_poste import (LaPosteAPIException,
                                   LaPosteUnauthorizedException)

from .helpers import la_poste_api, mock_requests


def test_successful_response(mock_requests, la_poste_api):
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = {
        "shipment": {"event": [{"label": "first_status"}, {"label": "second_status"}]}
    }

    response = la_poste_api.get_letter_details("number")
    assert response == "first_status"


def test_unauthorized_response(mock_requests, la_poste_api):
    mock_requests.return_value.status_code = 401

    with pytest.raises(LaPosteUnauthorizedException):
        la_poste_api.get_letter_details("number")


def test_la_poste_exception_if_connection_error(mock_requests, la_poste_api):
    mock_requests.side_effect = requests.exceptions.ConnectionError

    with pytest.raises(LaPosteAPIException):
        la_poste_api.get_letter_details("number")


@pytest.mark.parametrize(
    "return_value,expected",
    [
        ({}, "Unknown status"),
        ({"returnMessage": "Letter cannot be found"}, "Letter cannot be found"),
    ],
)
def test_get_broken_response(mock_requests, la_poste_api, return_value, expected):
    mock_requests.return_value.status_code = 404
    mock_requests.return_value.json.return_value = return_value

    response = la_poste_api.get_letter_details("number")
    assert response == expected
