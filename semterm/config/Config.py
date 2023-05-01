import configparser
import os


class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read(Config.get_config_file_path())

    def get(self):
        return self.config

    @staticmethod
    def get_config_file_path():
        src_dir = os.path.dirname(os.path.abspath(__file__))
        config_file = os.path.join(src_dir, "config.ini")
        return config_file
