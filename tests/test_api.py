import random
import time

import pytest

from app import db
from app.models.letter import Letter, LetterStatusHistory

from .helpers import client, json_of_response, mock_la_poste


def test_ping_pong(client):
    response = client.get("/v1/ping")

    assert response.status_code == 200
    assert json_of_response(response) == {"message": "pong"}


@pytest.mark.parametrize("tracking_number", [None, ""])
def test_create_letter_without_number(client, tracking_number):
    response = client.post("/v1/letters")

    assert response.status_code == 400
    assert json_of_response(response) == {
        "tracking_number": None,
        "message": "Tracking number should be specified.",
    }


def test_create_letter_successfully(client):
    tracking_number = random.randrange(1, 100)
    response = client.post("/v1/letters", json={"tracking_number": tracking_number})

    assert response.status_code == 200
    letter = Letter.query.filter_by(tracking_number=tracking_number).first()

    assert int(letter.tracking_number) == tracking_number
    assert letter.status[0].status == "New"


def test_cannot_create_letter_duplicate(client):
    tracking_number = random.randrange(1, 100)
    letter = Letter(tracking_number=tracking_number)
    db.session.add(letter)
    db.session.commit()

    response = client.post("/v1/letters", json={"tracking_number": tracking_number})

    assert response.status_code == 400
    assert json_of_response(response) == {
        "tracking_number": tracking_number,
        "message": "Letter is already present in DB.",
    }


def test_update_all_letters(client, mock_la_poste):

    for _ in range(1, 100):
        tracking_number = random.randrange(1, 1000)
        letter = Letter(tracking_number=tracking_number)
        db.session.add(letter)
        db.session.commit()

    response = client.put("/v1/letters")

    time.sleep(1)
    assert response.status_code == 200
    assert all(
        mock_la_poste.get_letter_details.return_value == status.status
        for status in LetterStatusHistory.query.all()
    )


def test_get_non_existing_letter(client):
    response = client.get("/v1/letters/test")

    assert response.status_code == 404
    assert json_of_response(response) == {
        "tracking_number": "test",
        "message": "Letter is not found.",
    }


def test_get_letter_successfully(client):
    tracking_number = random.randrange(1, 100)
    client.post("/v1/letters", json={"tracking_number": tracking_number})

    response = client.get(f"/v1/letters/{tracking_number}")

    assert response.status_code == 200
    assert json_of_response(response)["status_history"][0]["status"] == "New"


def test_update_letter_with_the_newest_status(client, mock_la_poste):
    tracking_number = random.randrange(1, 100)
    client.post("/v1/letters", json={"tracking_number": tracking_number})

    response = client.put(f"/v1/letters/{tracking_number}")

    assert response.status_code == 200
    assert (
        json_of_response(response)["message"]
        == mock_la_poste.get_letter_details.return_value
    )


def test_update_letter_with_the_same_status_just_updates_time(client, mock_la_poste):
    tracking_number = random.randrange(1, 100)
    client.post("/v1/letters", json={"tracking_number": tracking_number})

    client.put(f"/v1/letters/{tracking_number}")
    letter = Letter.query.filter_by(tracking_number=tracking_number).first()
    time_after_first_put = letter.status[0].last_update

    response = client.put(f"/v1/letters/{tracking_number}")

    time_after_second_put = letter.status[1].last_update

    assert response.status_code == 200
    assert len(letter.status) == 2
    assert time_after_first_put != time_after_second_put
