from config_local import Config as ConfigDev
from config import Config as ConfigBase


class Config(ConfigBase, ConfigDev):
    DEBUG = True
