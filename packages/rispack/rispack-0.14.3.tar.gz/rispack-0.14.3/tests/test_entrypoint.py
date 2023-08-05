import pytest
from unittest import mock

from rispack.entrypoint import get_function

def test_get_function():
    # Arrange
    expected_function = mock.Mock()
    jobs = mock.Mock()
    routes = mock.Mock(create_profile=expected_function)
    context = mock.Mock(function_name="RouteCreateProfile-XPTO")

    # Act
    result = get_function(jobs, routes, context)

    # Assert
    assert result == expected_function