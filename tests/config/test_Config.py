import configparser
from semterm.config.Config import Config
from unittest.mock import patch
import pytest


class TestConfig:
    @pytest.fixture(scope="class", autouse=True)
    def temp_dir(self, tmpdir_factory):
        tmpdir = tmpdir_factory.mktemp("config")
        tmp_config_file = tmpdir.join("config.ini")
        tmp_config_file.write("[example]\nkey=value\n")
        return tmp_config_file

    def test_config_initialization(self, temp_dir):
        # Patch the get_config_file_path to return the path of the temporary config file
        with patch(
            "semterm.config.Config.Config.get_config_file_path",
            return_value=temp_dir.strpath,
        ):
            config = Config()

        # Check if the config object is an instance of configparser.ConfigParser
        assert isinstance(config.config, configparser.ConfigParser)

        # Test if the config file is read correctly
        assert config.config.get("example", "key") == "value"

    def test_get_config_file_path(self, temp_dir):
        # Patch the get_config_file_path to return the path of the temporary config file
        with patch(
            "semterm.config.Config.Config.get_config_file_path",
            return_value=temp_dir.strpath,
        ):
            config = Config()
            actual_path = config.get_config_file_path()

        # Check if the mocked get_config_file_path method returns the path of the temporary config file
        assert actual_path == temp_dir.strpath

    def test_get(self):
        config = Config()
        assert isinstance(config.get(), configparser.ConfigParser)
