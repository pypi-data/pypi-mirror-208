import unittest
from unittest.mock import patch

from .client import FeatureFlagClient, feature_flags, mock_ff


@patch("flags_be_client.client.FeatureFlagClient.get_public_file_content")
@patch("flags_be_client.client.FeatureFlagClient.get_private_file_content")
def test_get_flag_with_identifier(mock_private_json, mock_public_json):
    mock_private_json.return_value = [
        {
            "id": 2,
            "name": "666",
            "active": True,
            "whitelist": ["*@sdl.com", "123@test.com"],
            "blacklist": ["666@sdl.com", "abc@test.com"],
        },
        {
            "id": 2,
            "name": "666",
            "active": False,
            "whitelist": ["*@sdl.com", "123@test.com", "777"],
            "blacklist": ["666@sdl.com", "abc@test.com"],
        },
    ]
    mock_public_json.return_value = []

    client = FeatureFlagClient()
    flag = client.is_enabled(flag_name="666", identifier="777")
    assert False == flag


def test_whitelist_blacklist_filter():
    client = FeatureFlagClient()
    flag = {
        "id": 2,
        "name": "666",
        "active": True,
        "whitelist": ["*@sdl.com", "123@test.com"],
        "blacklist": ["666@sdl.com", "abc@test.com"],
    }

    not_visible = client.check_is_visible(flag, identifier="666@sdl.com")
    assert not_visible == False

    is_visible = client.check_is_visible(flag, identifier="123@test.com")
    assert is_visible == True


def test_is_active():
    client = FeatureFlagClient()
    flag = {
        "id": 2,
        "name": "666",
        "active": False,
        "whitelist": ["*@sdl.com", "123@test.com"],
        "blacklist": ["666@sdl.com", "abc@test.com"],
    }

    not_visible = client.check_is_visible(flag, identifier="666@sdl.com")
    assert not_visible == False


@patch("flags_be_client.client.FeatureFlagClient.get_public_file_content")
@patch("flags_be_client.client.FeatureFlagClient.get_private_file_content")
def test_percentage(mock_private_json, mock_public_json):
    mock_private_json.return_value = [
        {
            "id": 2,
            "name": "666",
            "active": True,
            "whitelist": ["*@sdl.com", "123@test.com"],
            "blacklist": [],
            "percentage": 20,
        }
    ]
    mock_public_json.return_value = []

    client = FeatureFlagClient()

    count_identifiers = 10000
    identifiers = ["%s@sdl.com" % i for i in range(count_identifiers)]
    count_visible = 0
    for identifier in identifiers:
        if client.is_enabled("666", identifier=identifier):
            count_visible += 1
    # about 20% should be visible, but this is not exact
    twenty_percent = 2000

    assert (twenty_percent * 0.9) < count_visible < (twenty_percent * 1.1)


def test_mock_ff():
    assert not feature_flags.is_enabled("F1")
    assert not feature_flags.is_enabled("F2")

    with mock_ff(["F1"]):
        assert feature_flags.is_enabled("F1")
        assert feature_flags.is_enabled("F1", identifier="john@example.com")
        assert not feature_flags.is_enabled("F2")


class Testing(unittest.TestCase):
    def test_timed_cache(self):
        """Test the timed_cache decorator."""

        from .client import timed_cache

        import logging
        import time

        cache_logger = logging.getLogger("foo_log")

        @timed_cache(seconds=1)
        def cache_testing_function(num1, num2):
            cache_logger.info("Not cached yet.")
            return num1 + num2

        with self.assertLogs("foo_log", level="INFO") as cache_log:
            result1 = cache_testing_function(2, 3)
            self.assertEqual(cache_log.output[0], "INFO:foo_log:Not cached yet.")
            assert result1 == 5

            result2 = cache_testing_function(2, 3)
            assert len(cache_log.output) == 1
            assert result2 == 5

            time.sleep(1)

            result3 = cache_testing_function(2, 3)
            self.assertEqual(cache_log.output[1], "INFO:foo_log:Not cached yet.")
            assert result3 == 5
