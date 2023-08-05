import os
from http import HTTPStatus

import requests

from rispack.aws import get_signed_auth
from rispack.errors import RispackError
from rispack.handler import Request, Response
from rispack.handler.interceptors.base import BaseInterceptor
from rispack.logger import logger


class InvalidTokenEndpoint(RispackError):
    pass


class TokenInterceptor(BaseInterceptor):
    SETTINGS = {
        "header": "X-Authorization-Token",
        "authorizer_key": "profile_id",
        "param_name": "token",
    }

    def __init__(self, validate_pin):
        self.validate_pin = validate_pin
        self.endpoint = os.environ.get("TOKEN_AUTHORIZATION_URL")

        if not self.endpoint:
            raise InvalidTokenEndpoint

    def __call__(self, request: Request):
        id = request.authorizer.get(self.SETTINGS["authorizer_key"])
        token = self._find_header(request.headers)

        if not token:
            return Response.forbidden(f"Invalid {self.SETTINGS['header']} header")

        payload = {"token": token, self.SETTINGS["authorizer_key"]: id}

        response = requests.post(self.endpoint, auth=get_signed_auth(), json=payload)

        logger.debug(
            {
                "endpoint": self.endpoint,
                "message": "debug token interceptor",
                "payload": payload,
                "response": response,
            }
        )

        if response.status_code != HTTPStatus.OK:
            return Response.forbidden("Invalid TOKEN")

        return None

    def _find_header(self, headers):
        for header, value in headers.items():
            if header.lower() == self.SETTINGS["header"].lower():
                return value
