import platform
from configparser import ConfigParser
import os

root_folder = os.getcwd()
current_os = platform.system()

config = ConfigParser(comment_prefixes='/', allow_no_value=True)
if current_os == "Linux":
    config.read('config.ini')
else:
    config.read(os.path.join(root_folder, "config.ini"))


def get_config(key):
    return config['Configuration'].get(key)


