import os
import configparser

CONFIG_PATH = os.path.expanduser('~/.footprint.ini')


def footprint_config(config_path=CONFIG_PATH):

    if os.path.exists(CONFIG_PATH):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        return config


def print_conf_infomation():
    print("""
footprint needs "GITHUB_TOKEN" that Your Github Personal access Token from https://github.com/settings/tokens.
so, you need to put "GITHUB_TOKEN" to ~/.footprintconf.py, it is like the following.

~/.footprintconf.py
--------------------------
GITHUB_TOKEN = 'xxxxxxxxxxxxxxxxxxxxx'
""")
