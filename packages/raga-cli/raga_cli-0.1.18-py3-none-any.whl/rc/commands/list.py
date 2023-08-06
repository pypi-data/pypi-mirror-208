

import argparse
import logging
from rc.cli import log_setup

from rc.cli.command import CmdBase
from rc.cli.utils import get_repo
from rc.utils.request import get_repository, get_version


logger = logging.getLogger(__name__)

class CmdList(CmdBase):
    def __init__(self, args):
        super().__init__(args)
    
    def run(self):
        log_setup(self.args)
        repo = get_repo()
        tag = get_repository(repo)
        data = get_version(repo)
        if tag=="dataset":
            print(f"{'Commit id':<40}{'Commit message':<20}")
        else:
            print(f"{'Branch':<20}  {'Commit id':<45}{'Commit message':<20}")

        for commit in data:
            commit_id = commit["commit_id"]
            commit_message = commit["commit_message"]
            branch = ""
            if tag=="model":
                branch =  commit["branch"]
                print(f"{branch:<20}    {commit_id:<40}   {commit_message:<20}")
            else:
                print(f"{commit_id:<40}   {commit_message:<40}")
            
            

def add_parser(subparsers, parent_parser):
    REPO_HELP = "List versions"
    REPO_DESCRIPTION = (
        "List versions."
    )

    repo_parser = subparsers.add_parser(
        "list",
        parents=[parent_parser],
        description=REPO_DESCRIPTION,
        help=REPO_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    repo_parser.set_defaults(func=CmdList)