import argparse
import logging
from datetime import timedelta 
from timeit import default_timer as timer
import json
from rc.cli import log_setup

from rc.cli.command import CmdBase
from rc.cli.utils import run_command_on_subprocess,branch_commit_checkout
from rc.cli.utils import *
from rc.utils.folder_file import check_root_folder
from rc.utils.request import get_repo_commit_id, get_repository, get_repo_commit

logger = logging.getLogger(__name__)

class CmdGet(CmdBase):
    def __init__(self, args):
        super().__init__(args)
    def run(self):
        log_setup(self.args)
        start = timer()
        repo = get_repo()
        
        tag = get_repository(repo)
       
        version = self.args.version
        if not version:
            print("Files downloading...") 
            repo_commit = get_repo_commit(repo)
            if tag == "model":
                if check_git_add_untrack_files():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                if check_git_commit_files():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                if check_push_left():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                run_command_on_subprocess('git reset --hard')
                run_command_on_subprocess('git reset --hard {0}'.format(repo_commit['commit_id']))
                run_command_on_subprocess('git clean -fd')
            if tag == "dataset":
                if check_root_folder():
                    print("File should not be present directly in the root folder of a dataset.")
                    sys.exit()
                if check_git_add_untrack_files():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                if check_dvc_add_left():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                run_command_on_subprocess('git reset --hard')
                run_command_on_subprocess('git reset --hard {0}'.format(repo_commit['commit_id']))
                run_command_on_subprocess('git clean -fd')
                run_command_on_subprocess('dvc pull -f') 
            print("Files downloaded successfully") 
            logger.debug('DOWNLOAD TIME {0}'.format(timedelta(seconds=timer()-start))) 
        else:  
            version = self.args.version
            commit = get_repo_commit_id(json.dumps({"repo":repo, "version":version}))
            if not commit:
                print(f"Version {version} not found on server.")
                sys.exit()
            if tag == "model":
                if check_git_add_untrack_files():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                if check_git_commit_files():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                if check_push_left():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                user_input = input("Are you sure you want to get it? [y/n]").lower()
                if user_input == 'y':
                    run_command_on_subprocess('git reset --hard')
                    run_command_on_subprocess('git checkout {0}'.format(commit['branch']))
                    run_command_on_subprocess('git reset --hard {0}'.format(commit['commit_id']))
                    run_command_on_subprocess('git clean -fd')
                else:
                    print("Please enter valid input")
            else:
                if check_root_folder():
                    print("File should not be present directly in the root folder of a dataset.")
                    sys.exit()
                if check_git_add_untrack_files():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                if check_dvc_add_left():
                    print('Untracked files present. Push new files to repository to save.')
                    input("Press Enter to continue (Untracked files will be deleted) or Ctrl + C to cancel...")
                user_input = input("Are you sure you want to get it? [y/n]").lower()
                if user_input == 'y':
                    print("Files downloading...") 
                    run_command_on_subprocess('git reset --hard {}'.format(commit['commit_id'])) 
                    run_command_on_subprocess('dvc pull -f') 
                    run_command_on_subprocess('git clean -df') 
                    # run_command_on_subprocess('dvc pull -f')
                    print("Files downloaded successfully") 
                    logger.debug('DOWNLOAD TIME {0}'.format(timedelta(seconds=timer()-start))) 
                else:
                    print("Please enter valid input")

        return 0


def add_parser(subparsers, parent_parser):
    REPO_HELP = "Get File or folder. Use: `rctl get`"
    REPO_DESCRIPTION = (
        "Get File or folder. Use: `rctl get`"
    )

    repo_parser = subparsers.add_parser(
        "get",
        parents=[parent_parser],
        description=REPO_DESCRIPTION,
        help=REPO_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    repo_parser.add_argument(
        "-v", 
        "--version", 
        nargs="?", 
        default=None,
        type=int,
        help="Repo commit version",
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
    repo_parser.set_defaults(func=CmdGet)