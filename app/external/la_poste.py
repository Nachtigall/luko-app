from typing import Optional, Union

import requests
import requests.exceptions as request_exceptions

from app import app


class LaPosteUnauthorizedException(Exception):
    """Custom exception class. Used to notify when API keys are not authorized"""

    pass


class LaPosteAPIException(Exception):
    """Custom exception class. Used to notify an app when external API is down"""

    pass


class LaPosteAPI:
    def __init__(self, api_endpoint: str, api_key: str, language: Optional[str] = 'en_GB'):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.language = language

    @property
    def headers(self):
        return {"Accept": "application/json", "X-Okapi-Key": self.api_key}

    def get_letter_details(self, tracking_number: int) -> Union[str, Exception]:
        """
        Get letter details from LaPoste API
        :param tracking_number: letter tracking number which is tracked
        :return: If letter is found (200) - we return latest status. If not (400 or 404) - message status from LaPoste
        """
        try:
            response = requests.get(
                f"{self.api_endpoint}/idships/{tracking_number}?lang={self.language}",
                headers=self.headers,
            )

            if response.status_code == 401:
                app.logger.error("Unauthorized error occurred.")
                raise LaPosteUnauthorizedException()

            if response.status_code == 200:
                return response.json()["shipment"]["event"][0]["label"]
            elif response.status_code in [400, 404]:
                return response.json().get("returnMessage", "Unknown status")
        except (
            request_exceptions.ConnectionError,
            request_exceptions.Timeout,
            request_exceptions.HTTPError,
        ) as err:
            app.logger.error(err)
            raise LaPosteAPIException()
