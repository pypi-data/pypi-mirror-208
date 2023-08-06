import pytest

from unittest import mock
from unittest.mock import MagicMock, create_autospec
from organelle_segmenter_plugin.core.state import State, SegmenterModel


class TestRouter:
    def setup_method(self):
        self._state = State()

    def test_segmenter_model(self):
        # Assert
        assert self._state.segmenter_model is not None
        assert type(self._state.segmenter_model) == SegmenterModel
