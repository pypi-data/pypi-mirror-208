from abc import ABC, abstractmethod

from rispack.handler import Request


class BaseInterceptor(ABC):
    @classmethod
    def get_param(cls):
        return cls.get_settings("param_name")

    @classmethod
    def get_settings(cls, name):
        return cls.SETTINGS.get(name)

    @abstractmethod
    def __call__(self, request: Request):
        pass
