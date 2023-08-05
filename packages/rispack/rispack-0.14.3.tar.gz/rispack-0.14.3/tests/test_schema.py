import pytest

from rispack.schemas import BaseSchema, dataclass
from dataclasses import field

@dataclass
class UserTest(BaseSchema):
    id: str
    name: str
    age: int = field(default=None)


class TestBaseSchema:
    def test_load(self):
        user = {"name": "John", "id": "1234-1234-1234-1234"}

        loaded = UserTest.load(user)

        assert loaded.name == user["name"]
        assert loaded.id == user["id"]

    def test_load_exclude_unknown_fields(self):
        user = {"name": "John", "id": "1234-1234-1234-1234", "password": "123mudar"}

        loaded = UserTest.load(user)

        assert loaded.name == user["name"]
        assert loaded.id == user["id"]

    def test_load_accept_marshmallow_load_args(self):
        user1 = {
            "name": "John",
            "id": "1234-1234-1234-1234",
        }

        user2 = {
            "name": "John",
            "id": "1234-1234-1234-1234",
        }

        users = [user1, user2]

        loaded = UserTest.load(users, many=True)

        assert isinstance(loaded, list)

    def test_load_dump_if_base_schema(self):
        payload = UserTest.load(
            {"name": "Satoshi Nakamoto", "id": "1234-1234-1234-1234"}
        )

        assert UserTest.load(payload) is not None

    def test_dump(self):
        user = UserTest(
            name="John",
            id="1234-1234-1234-1234",
        )

        user_dict = user.dump()

        assert isinstance(user_dict, dict)
        assert user_dict["name"] == user.name
        assert user_dict["id"] == user.id
        assert user_dict["age"] == None

    def test_dump_with_arguments(self):
        user = UserTest(
            name="John",
            id="1234-1234-1234-1234",
        )

        user_dict = user.dump(only=["name"])

        assert user_dict["name"] == user.name
        assert user_dict.get("id") is None

        user_dict = user.dump(exclude=["name"])

        assert user_dict.get("name") is None
        assert user_dict["id"] == user.id
        assert user_dict["age"] == None


    def test_dump_with_skip_none(self):
        user = UserTest(
            name="John",
            id="1234-1234-1234-1234",
        )

        user_dict = user.dump(skip_none=True)

        with pytest.raises(KeyError):
            user_dict["age"]
