from enum import Enum

from rispack.handler import Request, Response
from rispack.handler.interceptors import BaseInterceptor


class RoleInterceptor(BaseInterceptor):
    SETTINGS = {
        "param_name": "role",
        "deprecated": True,
    }

    def __init__(self, role):
        if isinstance(role, Enum):
            role = role.value

        self.role = role

    def __call__(self, request: Request):
        role_payload = request.authorizer.get("roles") or ""

        user_roles = role_payload.split(",")

        if self.role not in user_roles:
            return Response.forbidden(f"Authorizer does not have role '{self.role}'.")
