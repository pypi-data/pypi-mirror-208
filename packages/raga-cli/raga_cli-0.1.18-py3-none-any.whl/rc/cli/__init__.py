import json
import logging
import os
import subprocess
from rc.cli.utils import get_repo
from rc.utils.request import RctlValidRequestError, get_config_value_by_key, update_repo_lock
from rc.utils import DEBUG
logger = logging.getLogger(__name__)
level = logging.INFO

def log_setup(args = None):
    if DEBUG:
        level = logging.DEBUG
        logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')     
    if args:
        if args.output:
            level = logging.DEBUG
            logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S') 

log_setup()
class RctlParserError(Exception):
    """Base class for CLI parser errors."""
    def __init__(self):
        logger.error("Parser error")
        super().__init__("Parser error")

class RctlValidReqError(Exception):
    def __init__(self, msg, *args):
        assert msg
        self.msg = msg
        logger.error(msg)
        super().__init__(msg, *args)

def parse_args(argv=None):
    from .parser import get_main_parser
    try:
        parser = get_main_parser()
        args = parser.parse_args(argv)
        args.parser = parser
        return args
    except RctlParserError as exc:
        pass

def valid_requirement():
    try:        
        subprocess.run(['gh', '--version'], capture_output=True)
    except OSError as err:        
        raise RctlValidRequestError('ERROR: git hub cli not found! Please install git hub cli from https://cli.github.com')
    try:        
        subprocess.run(['git', '--version'], capture_output=True)
    except OSError as err:        
        raise RctlValidRequestError('git not found! Please install git')
        

def main(argv=None):
    try:
        os.environ['GH_TOKEN'] = get_config_value_by_key('gh_token')
        valid_requirement()
        args = parse_args(argv)
        cmd = args.func(args)
        cmd.do_run()
    except KeyboardInterrupt as exc:
        pass
    except RctlValidRequestError as exc:
        pass
    except Exception as exc:
       logger.exception(exc)
    
