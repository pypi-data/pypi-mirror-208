import appdirs
import configparser
import os

"""
    maintain the configuration for the gpt-convo-reade application

    The configuration may be persisted in a file.

    In normal use, that file is `gpt-convo-reader/config.ini`
    in the user's config directory.

    Typical user config directories are:
        Mac OS X:               same as user_data_dir:  ~/Library/Application Support/<AppName>
        Unix:                   ~/.config/<AppName>     # or in $XDG_CONFIG_HOME, if defined
        Win *:                  same as user_data_dir
    """

class Configuration:
    def __init__(self, zip_directory = '.', save_directory = '.', prefix = ''):
        self.zip_directory = zip_directory
        self.save_directory = save_directory
        self.prefix = prefix


def get_configuration() -> Configuration:
    config_directory = appdirs.user_config_dir("gpt-convo-reader")
    config_file_path = os.path.join(config_directory, "config.ini")
    if os.path.exists(config_file_path):
        # read configuration file using ConfigParser and  create configuration object
        config = configparser.ConfigParser()
        config.read(config_file_path)
        configuration = Configuration(
            zip_directory = config['default directory locations']['zip directory'],
            save_directory = config['default directory locations']['save directory'],
            prefix = config['default directory locations']['prefix'])
    else:
        configuration = Configuration() # the default
    return configuration






