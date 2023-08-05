import pytest
from unittest.mock import MagicMock
from rispack.events import BaseEvent
from rispack.actions import BaseAction
from rispack.schemas import dataclass
from uuid import UUID, uuid4
from dataclasses import field
from unittest.mock import patch


@dataclass
class SampleEvent(BaseEvent):
    name: str
    id: UUID = field(default_factory=uuid4)

    def get_type(self):
        return "SampleEvent"

    def get_version(self):
        return "1.0"

    def get_aggregate_id(self):
        return "test-aggregate-id"

class SampleAction(BaseAction):
    def call(self, params):
        self.publish(SampleEvent, params)

        return params["name"]

    def _scoped(self, params):
        return self.call(params)


class TestBaseAction:
    def test_publish(self):
        action = SampleAction()
        params = {"name": "Satoshi Nakamoto"}

        with patch.object(SampleEvent, 'publish', return_value=MagicMock()) as mock_publish:
            with patch.object(SampleAction,'__new__', return_value=action):
                    SampleAction.run(params)

                    assert len(action.events) == 0
                    mock_publish.assert_called_once()

    def test_run(self):
        params = {"name": "Satoshi Nakamoto"}
        action = SampleAction()
        SampleAction._scoped = MagicMock(return_value=action.call(params))

        action_response = action.run(params=params)

        assert action_response == params["name"]
        action._scoped.assert_called_once_with(params)
