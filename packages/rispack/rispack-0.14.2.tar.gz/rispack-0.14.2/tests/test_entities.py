import pytest
from unittest import mock

from rispack.entities import BaseEntity
from rispack.schemas import dataclass

class LoanStore:
    pass

@dataclass
class Loan(BaseEntity):
    name: str


class TestBaseEntity:
    def test_store_method_returns_store_instance(self):
        with mock.patch("rispack.entities.import_module") as mock_import_module:
            mock_import_module.return_value = mock.MagicMock(LoanStore=LoanStore)

            instance = Loan.store()

        assert isinstance(instance, LoanStore)

    def test_store_method_returns_cached_instance(self):
        with mock.patch("rispack.entities.import_module") as mock_import_module:
            mock_import_module.return_value = mock.MagicMock(LoanStore=LoanStore)

            instance1 = Loan.store()
            instance2 = Loan.store()

        assert instance1 == instance2
