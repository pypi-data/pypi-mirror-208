import logging
import os
import configparser
logger = logging.getLogger(__name__)

def create_rc_folder(repo, configs = None):
    """
    Creates a .rc folder in the current directory and a config file inside it.
    """
    owd = os.getcwd()
    os.chdir(f"{owd}/{repo}")   
    rc_folder = os.path.join(os.getcwd(), '.rc')
    if not os.path.exists(rc_folder):
        os.makedirs(rc_folder)
    config_file = os.path.join(rc_folder, 'config')
    if not os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.add_section('settings')
        logger.debug("Adding config")
        if configs:
            for key, value in configs.items():
                config.set('settings', str(key), str(value))
        with open(config_file, 'w') as f:
            config.write(f)
    os.chdir(owd)

def get_config_value(key):
    """
    Gets the value associated with the given key in the config file.
    """
    logger.debug("Getting Config")
    rc_folder = os.path.join(os.getcwd(), '.rc')
    config_file = os.path.join(rc_folder, 'config')
    if not os.path.exists(config_file):
        return None
    config = configparser.ConfigParser()
    config.read(config_file)
    if 'settings' in config and key in config['settings']:
        return config['settings'][key]
    else:
        return None

def set_config_value(key, value, cwd=None):
    """
    Sets the value associated with the given key in the config file.
    """
    if cwd:
        owd = os.getcwd()
        os.chdir(f"{owd}/{cwd}") 
    logger.debug("Setting Config")
    rc_folder = os.path.join(os.getcwd(), '.rc')
    config_file = os.path.join(rc_folder, 'config')
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
    if 'settings' not in config:
        config.add_section('settings')
    config.set('settings', str(key), str(value))
    with open(config_file, 'w') as f:
        config.write(f)
    if cwd:
        os.chdir(owd)