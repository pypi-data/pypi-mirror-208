import json

from copy import copy
from unittest import mock

import pytest

from rispack.database import Database, DatabaseCredentialError, Session

conn = {
    "user": "dbuser",
    "endpoint": "dbendpoint.com",
    "name": "dbname",
    "secret_arn": "arn:us-east-1:123",
}


class TestDatabase:
    def test_required_field(self, monkeypatch):
        fields = ["user", "endpoint", "name", "secret_arn"]

        for f in fields:
            conn2 = copy(conn)
            conn2[f] = None
            envvar = "".join(["DB_", f.upper()])
            monkeypatch.delenv(envvar, raising=False)


            with pytest.raises(DatabaseCredentialError):
                Database(**conn2)

    @mock.patch("rispack.database.get_secret")
    def test_get_connection_string(self, mock_secret):
        password = "@bcd3"
        mock_secret.return_value = json.dumps({"password": password})

        db = Database(**conn)

        connstr = f"postgresql+pg8000://dbuser:{password}@dbendpoint.com:5432/dbname"
        assert db.get_connection_string() == connstr

    @mock.patch("rispack.database.create_engine")
    @mock.patch("rispack.database.get_secret")
    def test_session(self, mock_secret, mock_create_engine):
        password = "@bcd3"
        mock_secret.return_value = json.dumps({"password": password})

        mock_create_engine.return_value = []

        db = Database(**conn)

        assert type(db.session) is Session

    @mock.patch("rispack.database.create_engine")
    @mock.patch("rispack.database.get_secret")
    def test_session_dispose(self, mock_secret, mock_create_engine):
        password = "@bcd3"
        mock_secret.return_value = json.dumps({"password": password})

        mock_create_engine.return_value = []

        db = Database(**conn)

        initial_session = db.session
        db.dispose_session()

        assert db.session != initial_session
