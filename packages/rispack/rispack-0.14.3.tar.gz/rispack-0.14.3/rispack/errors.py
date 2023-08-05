class RispackError(Exception):
    pass


class InvalidRoleError(RispackError):
    pass


class InvalidResponseError(RispackError):
    pass


class NotFoundError(RispackError):
    pass


class BadRequestError(RispackError):
    pass


class UnhandledSourceError(RispackError):
    pass


class EventBusNotSetError(RispackError):
    pass


class InvalidInterceptorError(RispackError):
    pass
