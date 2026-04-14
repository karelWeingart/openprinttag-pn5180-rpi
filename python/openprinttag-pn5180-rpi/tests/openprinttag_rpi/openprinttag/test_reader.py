from unittest.mock import Mock
import openprinttag_rpi.openprinttag.reader as reader_module_for_spy
from openprinttag_rpi.openprinttag.reader import search_tag
from openprinttag_rpi.pn5180_rpi.sensor import ExtendedISO15693Sensor
from openprinttag_rpi.common.enum import TagReadEvent
from openprinttag_rpi.models.event_dto import EventDto
import pytest
import pytest_mock

_invalid_uid = "invalid_uid"
_valid_uid = "E007C4A509480104"


@pytest.fixture
def mock_reader(mocker: pytest_mock.plugin.MockerFixture) -> Mock:
    mock = mocker.Mock(spec=ExtendedISO15693Sensor)
    return mock


@pytest.fixture
def make_mock_has_openprinttag_bin(mocker: pytest_mock.plugin.MockerFixture) -> Mock:
    def _factory(side_effect: list[bool]) -> Mock:
        return mocker.patch(
            "openprinttag_rpi.openprinttag.reader.has_openprinttag_bin",
            side_effect=side_effect,
        )

    return _factory


@pytest.fixture
def make_spy_from_reader_module(mocker: pytest_mock.plugin.MockerFixture) -> Mock:
    def _factory(method_name: str) -> Mock:
        return mocker.spy(reader_module_for_spy, method_name)

    return _factory


def test_search_tag_has_openprinttag_bin(
    mocker: pytest_mock.plugin.MockerFixture,
    mock_reader: Mock,
    make_mock_has_openprinttag_bin: Mock,
) -> None:
    """Test the search_tag function."""
    make_mock_has_openprinttag_bin([True])
    _uid = search_tag(mock_reader)
    assert _uid is None


def test_search_tag_invalid_uid_then_has_openprinttag_bin(
    mocker: pytest_mock.plugin.MockerFixture,
    mock_reader: Mock,
    make_mock_has_openprinttag_bin: Mock,
    make_spy_from_reader_module: Mock,
) -> None:
    """Test the search_tag function."""
    make_mock_has_openprinttag_bin([False, True])
    mock_reader.read_tag.return_value = _invalid_uid
    spy_register_event = make_spy_from_reader_module("register_event")

    _uid = search_tag(mock_reader)
    _expected_event_dto = EventDto(
        event_type=TagReadEvent.TAG_UID_INVALID, data={"uid": _invalid_uid}
    )
    spy_register_event.assert_called_once_with(_expected_event_dto)
    assert _uid is None


def test_search_tag_valid_uid(
    mocker: pytest_mock.plugin.MockerFixture,
    mock_reader: Mock,
    make_mock_has_openprinttag_bin: Mock,
    make_spy_from_reader_module: Mock,
) -> None:
    """Test the search_tag function."""
    make_mock_has_openprinttag_bin([False])
    mock_reader.read_tag.return_value = _valid_uid
    spy_register_event = make_spy_from_reader_module("register_event")

    _uid = search_tag(mock_reader)
    _expected_event_dto = EventDto(
        event_type=TagReadEvent.TAG_DETECTED, data={"uid": _uid}
    )
    spy_register_event.assert_called_once_with(_expected_event_dto)
    assert _uid == _valid_uid
