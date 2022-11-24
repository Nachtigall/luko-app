import datetime
import json
from concurrent.futures import ThreadPoolExecutor

from flask import Blueprint, copy_current_request_context, request

from app import app, db
from app.models.letter import Letter, LetterStatusHistory

from ..external.la_poste import (
    LaPosteAPI,
    LaPosteAPIException,
    LaPosteUnauthorizedException,
)

executor = ThreadPoolExecutor()

first_version = Blueprint("v1", __name__, url_prefix="/v1")
la_poste_api = LaPosteAPI(
    app.config["LA_POST_API_ENDPOINT"],
    app.config["LA_POST_API_KEY"],
    app.config["LA_POST_API_LANGUAGE"],
)


@first_version.errorhandler(LaPosteUnauthorizedException)
def unauthorized_error(e):
    return {"message": "Unauthorized error. You need to provide correct API keys."}, 401


@first_version.errorhandler(LaPosteAPIException)
def internal_server_error(e):
    return {
        "message": "Looks like external tracking API is down. Please, try again later."
    }, 500


@first_version.route("/ping", methods=["GET"])
def ping():
    """Just dummy response"""
    return json.dumps({"message": "pong"}), 200


@first_version.route("/letters", methods=["POST", "PUT"])
def setup_create_letter():
    """
    Endpoint to create/update all letters
    :return: json response with letter data if it's created/update successfully. Otherwise - 400 error
    """
    if request.method == "POST":
        letter_data = request.get_json()

        tracking_number = letter_data.get("tracking_number", None) if letter_data else None
        if not tracking_number:
            return (
                json.dumps(
                    {
                        "tracking_number": None,
                        "message": "Tracking number should be specified.",
                    }
                ),
                400,
            )

        if bool(Letter.query.filter_by(tracking_number=tracking_number).first()):
            return (
                json.dumps(
                    {
                        "tracking_number": tracking_number,
                        "message": "Letter is already present in DB.",
                    }
                ),
                400,
            )

        letter = Letter(tracking_number=tracking_number)
        db.session.add(letter)
        db.session.flush()

        letter_history = LetterStatusHistory(letter_id=letter.id)
        db.session.add(letter_history)
        db.session.commit()

        return (
            json.dumps(
                {
                    "tracking_number": letter.tracking_number,
                    "message": "Letter has been created",
                }
            ),
            200,
        )
    else:
        app.logger.debug("Bulk letters update has been started")

        @copy_current_request_context
        def get_letter_status(trck_number):
            update_get_letter_status(trck_number)

        executor.map(
            get_letter_status, [letter.tracking_number for letter in Letter.query.all()]
        )

        app.logger.debug("Bulk letters update has been finished")
        return {
            "message": "Update for all letters has started. Results will be available shortly."
        }


@first_version.route("/letters/<tracking_number>", methods=["GET", "PUT"])
def update_get_letter_status(tracking_number: int):
    """
    Endpoint to get/update letter by tracking number
    :param tracking_number: letter tracking number
    :return: json response with the newest letter status if letter is found, else 404 response
    """
    letter = Letter.query.filter_by(tracking_number=tracking_number).first()
    if not letter:
        return (
            json.dumps(
                {"tracking_number": tracking_number, "message": "Letter is not found."}
            ),
            404,
        )

    if request.method == "GET":
        return json.dumps(letter.serialize(), default=str)

    letter_status = la_poste_api.get_letter_details(tracking_number)

    letter = Letter.query.filter_by(tracking_number=tracking_number).first()
    if letter.status:
        latest_status = sorted(
            letter.status, key=lambda sh: sh.last_update, reverse=True
        )[0]
    else:
        latest_status = None

    if latest_status and latest_status.status == letter_status:
        # if we have the latest status already in DB - just update time. Otherwise - store the newest
        app.logger.info(
            f"We have already the newest status in DB for letter {tracking_number} - so just updating time"
        )
        latest_status.last_update = datetime.datetime.utcnow()
        db.session.commit()
    else:
        letter_history = LetterStatusHistory(letter_id=letter.id, status=letter_status)
        app.logger.info(f"Stored the newest status for {tracking_number}")
        db.session.add(letter_history)
        db.session.commit()

    return (
        json.dumps({"tracking_number": tracking_number, "message": letter_status}),
        200,
    )
