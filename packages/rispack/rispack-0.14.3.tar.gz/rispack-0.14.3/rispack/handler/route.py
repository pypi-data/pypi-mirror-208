from functools import wraps

from marshmallow.exceptions import ValidationError

from rispack.errors import BadRequestError, InvalidInterceptorError, NotFoundError
from rispack.logger import logger

from .interceptors import (
    BaseInterceptor,
    OtpInterceptor,
    PinInterceptor,
    RoleInterceptor,
    ScopeInterceptor,
    TokenInterceptor,
)
from .request import Request
from .response import Response

_INTERCEPTORS = [
    RoleInterceptor,
    PinInterceptor,
    OtpInterceptor,
    TokenInterceptor,
    ScopeInterceptor,
]


def add_interceptor(klass):
    _INTERCEPTORS.append(klass)


def route(*args, **kwargs):
    # looking for interceptors params, e.g @route(scope="user.creation")
    route_interceptors = _parse_interceptors(kwargs)

    def inner(func):
        @wraps(func)
        def wrapper(event, context=None):
            logger.debug(event)

            try:
                request = Request(event)
                intercepted = False

                for interceptor in route_interceptors:
                    if interceptor.get_settings("deprecated"):
                        logger.warning(
                            f"[DEPRECATION NOTICE] The interceptor {type(interceptor).__name__} is deprecated."
                        )

                    result = interceptor(request)

                    if isinstance(result, Response):
                        logger.debug(f"Intercepted by {str(interceptor)}")
                        intercepted = True
                        break

                if not intercepted:
                    result = func(request)

                if not isinstance(result, Response):
                    result = Response.internal_server_error("Invalid response error")

            except ValidationError as e:
                logger.debug(str(e))

                errors = _get_validation_errors(e.messages)

                result = Response.bad_request(errors)

            except BadRequestError as e:
                logger.debug(str(e))

                result = Response.bad_request(str(e))

            except NotFoundError as e:
                logger.debug(str(e))

                error = e.args[0]
                result = Response.not_found(error)

            except Exception as e:
                logger.exception(e)

                result = Response.internal_server_error()

            return result.dump()

        return wrapper

    # args[0] is the function itself when called
    # without parenthesis e.g. @route. This enables
    return inner if route_interceptors else inner(args[0])


def _get_validation_errors(fields):
    errors = []
    for key, value in fields.items():
        errors.append(
            {
                "id": f"invalid_{key}",
                "message": value[0],
                "field": key,
            }
        )
    return errors


def _parse_interceptors(kwargs):
    interceptors = []

    for interceptor in _INTERCEPTORS:
        if not issubclass(interceptor, BaseInterceptor):
            raise InvalidInterceptorError(
                f"Interceptor {interceptor.__name__} must inherit from BaseInterceptor"
            )

        if not interceptor.get_param():
            raise InvalidInterceptorError(
                f"Interceptor {interceptor.__name__} must have 'param_name' item on SETTINGS dict."
            )

        param = interceptor.get_param()
        route_params = kwargs.get(param)

        if route_params:
            interceptors.append(interceptor(route_params))

    return interceptors
