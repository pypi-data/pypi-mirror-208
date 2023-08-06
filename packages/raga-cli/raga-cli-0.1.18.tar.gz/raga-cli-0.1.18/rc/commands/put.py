import argparse
import logging


from rc.cli.command import CmdBase
from rc.cli.utils import *
from rc.cli import log_setup
from rc.repo.put import *
from rc.utils.config import get_config_value
from rc.utils.request import RctlValidRequestError

logger = logging.getLogger(__name__)

class CmdPut(CmdBase):
    def __init__(self, args):
        super().__init__(args)
        self.dirs = None
        if not getattr(self.args, "message", None):                               
            raise RctlValidRequestError("Error: Please provide a message, -m")
        if getattr(self.args, "path", None):
            self.dirs = [self.args.path]
        else:
            self.dirs = get_all_data_folder()         

    def run(self):      
        log_setup(self.args)
        valid_cwd_rc()
        self.args.path = self.dirs
        valid_dot_dvc_with_folder(self.args.path)
        put(self.args) 
        return 0


def add_parser(subparsers, parent_parser):
    REPO_HELP = "Put File or folder. Use: `rc put <file or folder path> -m <commit message>`"
    REPO_DESCRIPTION = (
        "Put File or folder. Use: `rc put <file or folder path> -m <commit message>`"
    )

    repo_parser = subparsers.add_parser(
        "put",
        parents=[parent_parser],
        description=REPO_DESCRIPTION,
        help=REPO_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    repo_parser.add_argument(
        "-m", 
        "--message", 
        nargs="?", 
        help="Commit message",
    )

    repo_parser.add_argument(
        "path", 
        nargs="?", 
        default=None,
        help="File or Folder path",
    )

    repo_parser.add_argument(
        "-o", 
        "--output", 
        type=bool, 
        nargs='?',
        const=True, 
        default=False,
        help="Output debug",
    )
    
 
    
    repo_parser.set_defaults(func=CmdPut)
