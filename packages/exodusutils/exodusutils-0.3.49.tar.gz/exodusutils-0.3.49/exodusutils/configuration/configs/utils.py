import os
from configparser import ConfigParser


def get_configs():
    if os.path.isfile("config.ini"):
        config = ConfigParser()
        config.read("config.ini")
        return config
    else:
        return None
