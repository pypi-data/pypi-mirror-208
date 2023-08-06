import json
import logging
import os
import colorama
from pathlib import Path
import pathlib

from rc.utils.config import get_config_value


RC_BASE_URL = "http://52.66.16.12:8092/v1/api"
RC_WEB_BACKEND_URL = 'http://52.66.16.12:8080/api'
RC_INFLUX_BACKEND_URL = 'http://52.66.16.12:8081/api'

BASE_URL = get_config_value('base_url')
WEB_BACKEND_URL = get_config_value('web_backend_url')
INFLUX_BACKEND_URL = get_config_value('influx_backend_url')

DEBUG = False
RCTL_PATH = '.rc'
RCTL_LOG_PATH = f'{RCTL_PATH}/logs'
RCTL_LOG_FILE = f'{RCTL_LOG_PATH}/rc.log'


def format_link(link):
    return "<{blue}{link}{nc}>".format(
        blue=colorama.Fore.CYAN, link=link, nc=colorama.Fore.RESET
    )

def relpath(path, start=os.curdir):
    path = os.fspath(path)
    start = os.path.abspath(os.fspath(start))

    # Windows path on different drive than curdir doesn't have relpath
    if os.name == "nt":
        # Since python 3.8 os.realpath resolves network shares to their UNC
        # path. So, to be certain that relative paths correctly captured,
        # we need to resolve to UNC path first. We resolve only the drive
        # name so that we don't follow any 'real' symlinks on the path
        def resolve_network_drive_windows(path_to_resolve):
            drive, tail = os.path.splitdrive(path_to_resolve)
            return os.path.join(os.path.realpath(drive), tail)

        path = resolve_network_drive_windows(os.path.abspath(path))
        start = resolve_network_drive_windows(start)
        if not os.path.commonprefix([start, path]):
            return path
    return os.path.relpath(path, start)

def create_folder(path):
    path = Path(path)
    if not path.is_dir():        
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)

def get_local_json(file_path):
    file_path = '{0}'.format(file_path)
    with open(file_path, 'r') as json_file:
        data = json_file.read()
        obj = json.loads(data)
    return obj

def json_save_to_local(json_obj, dest_path):
    with open(dest_path, 'w', encoding='utf-8') as f:
        json.dump(json_obj, f, ensure_ascii=False, indent=4)

