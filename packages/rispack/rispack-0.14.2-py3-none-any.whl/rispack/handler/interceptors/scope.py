from enum import Enum
from typing import Any, List

from rispack.handler import Request, Response
from rispack.handler.interceptors import BaseInterceptor


class ScopeInterceptor(BaseInterceptor):
    SETTINGS = {
        "param_name": "scope",
    }

    def __init__(self, scope: Enum | str):
        if isinstance(scope, Enum):
            scope = scope.value

        self.scope = scope

    def __call__(self, request: Request):
        payload = request.authorizer.get("scopes") or ""

        user_scopes = payload.split(",")

        if self.scope not in user_scopes:
            return Response.forbidden(
                f"Missing scope '{self.scope}' on the current session."
            )
