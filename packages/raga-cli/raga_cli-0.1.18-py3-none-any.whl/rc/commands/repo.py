import argparse
import json
import logging
import os
from datetime import timedelta
import sys 
from timeit import default_timer as timer
import os, pwd

from rc.cli.command import CmdBase
from rc.cli.utils import current_commit_hash, folder_exists, is_repo_exist_in_gh, run_command_on_subprocess, repo_name_valid, get_git_url, upload_model_file_list_json
from rc.utils import RC_BASE_URL, RC_INFLUX_BACKEND_URL, RC_WEB_BACKEND_URL
from rc.utils.config import create_rc_folder, set_config_value
from rc.utils.request import RctlValidRequestError, get_config_value_by_key, create_repository, create_repo_lock, get_repository, insert_repo_commit
from rc.cli import log_setup

logger = logging.getLogger(__name__)
   
 

"""
----------------------------
***Bucket Name Validation***
----------------------------
Bucket names should not contain upper-case letters
Bucket names should not contain underscores (_)
Bucket names should not end with a dash
Bucket names should be between 3 and 63 characters long
Bucket names cannot contain dashes next to periods (e.g., my-.bucket.com and my.-bucket are invalid)
Bucket names cannot contain periods - Due to our S3 client utilizing SSL/HTTPS, Amazon documentation indicates that a bucket name cannot contain a period, otherwise you will not be able to upload files from our S3 browser in the dashboard.
"""

class RepoMain():
    def __init__(self) -> None:
        self.CLOUD_STORAGE_BUCKET = get_config_value_by_key('bucket_name')
        self.CLOUD_STORAGE_DIR = get_config_value_by_key('cloud_storage_dir')
        self.CLOUD_STORAGE_LOCATION = f"s3://{self.CLOUD_STORAGE_BUCKET}/{self.CLOUD_STORAGE_DIR}"
        self.INITIAL_COMMIT = get_config_value_by_key('git_initial_commit')
        self.GIT_BRANCH = get_config_value_by_key('git_initial_branch')
        self.GIT_ORG = get_config_value_by_key('git_org')
        self.AUTH_TOKEN = get_config_value_by_key('auth_token')
        self.TAGS = {"dataset", "model"}
        self.created_by = pwd.getpwuid(os.getuid()).pw_name 

    def run_git_commands(self,repo_name, repo_tag):
        run_command_on_subprocess("git add .rc", repo_name)       
        run_command_on_subprocess("git commit -m '{0}' -a".format(self.INITIAL_COMMIT), repo_name)    
        run_command_on_subprocess("git branch -M {0}".format(self.GIT_BRANCH), repo_name)    
        run_command_on_subprocess("git push --set-upstream origin {0}".format(self.GIT_BRANCH), repo_name)

    def run_repo_create_subprocesses(self,repo_name, repo_tag):     
        logger.debug(f"Repository Name: {repo_name}")
        secret_key = get_config_value_by_key('remote_storage_secret_key')
        access_key = get_config_value_by_key('remote_storage_access_key')
        if repo_tag =="dataset":
            run_command_on_subprocess("gh config set git_protocol ssh")  
            run_command_on_subprocess("gh repo create {0}/{1} --private --clone".format(self.GIT_ORG, repo_name))    
            run_command_on_subprocess("dvc init", repo_name)    
            run_command_on_subprocess("dvc remote add -d {0} {1}/{2} -f".format(self.CLOUD_STORAGE_BUCKET, self.CLOUD_STORAGE_LOCATION, repo_name), repo_name)           
            run_command_on_subprocess("dvc remote modify {0} secret_access_key {1}".format(self.CLOUD_STORAGE_BUCKET,secret_key ), repo_name)         
            run_command_on_subprocess("dvc remote modify {0} access_key_id {1}".format(self.CLOUD_STORAGE_BUCKET, access_key), repo_name)        
            run_command_on_subprocess("dvc config core.autostage true", repo_name)            
        if repo_tag == "model":
            run_command_on_subprocess("gh config set git_protocol ssh")  
            run_command_on_subprocess("gh repo create {0}/{1} --private --clone".format(self.GIT_ORG, repo_name)) 
            run_command_on_subprocess("touch README.md", repo_name)      
            run_command_on_subprocess("git add README.md", repo_name)       

        configs = {
            "repo":repo_name,
            "git_org":self.GIT_ORG,
            "remote_bucket":self.CLOUD_STORAGE_BUCKET,
            "remote_bucket_dir":self.CLOUD_STORAGE_DIR,
            "remote_bucket_location":self.CLOUD_STORAGE_LOCATION,
            "secret_key":secret_key,
            "access_key":access_key,
            "version":0,
            "repo_id":"", 
            "tag":repo_tag,
            "auth_token":self.AUTH_TOKEN,
            "base_url": RC_BASE_URL,
            "web_backend_url": RC_WEB_BACKEND_URL,
            "influx_backend_url": RC_INFLUX_BACKEND_URL,
            "org_id":18,
            "project_id":2
        }  
        create_rc_folder(repo_name, configs)

    
    def create_repo(self, args):
        print("Repo creating...")  
        if self.check_git_init():
            print("The repo creating process inside the repository is not possible.")
            sys.exit(50) 
        logger.debug(f"START CREATE REPO COMMAND")
        repository_name = args.name    
        repository_tag = args.tag 
        if is_repo_exist_in_gh("{0}/{1}".format(self.GIT_ORG, repository_name)):
            print("The repo creating process could not be completed because the repo already exists. Please rename repo and try again.")
            sys.exit(50)

        if folder_exists(repository_name):
            print("The repo creating process could not be completed because the directory already exists. Please rename repo and try again.")
            sys.exit(50)

        if repository_tag not in self.TAGS:
            logger.error("'{0}' tag is not available. Please select from {1}".format(repository_tag, self.TAGS))
            sys.exit(50)   

        
        self.run_repo_create_subprocesses(repository_name, repository_tag)
        git_repo = get_git_url(repository_name)
        
        if repository_tag == "dataset":

            s3_repo = "{1}/{2}".format(self.CLOUD_STORAGE_BUCKET, self.CLOUD_STORAGE_LOCATION, repository_name)  

            req_body = json.dumps({
                "repo_name":repository_name,
                "tag":repository_tag,
                "created_by":self.created_by,
                "git_repo":git_repo.replace('\n', ''),
                "remote_storage_url":s3_repo,
            })

            logger.debug(req_body)

        if repository_tag == "model":
            req_body = json.dumps({
                "repo_name":repository_name,
                "tag":repository_tag,
                "created_by":self.created_by,
                "git_repo":git_repo.replace('\n', ''),
            })
            logger.debug(req_body)

        created_repo_data = create_repository(req_body)
        set_config_value("repo_id", created_repo_data['id'], repository_name)
        
        if repository_tag == "dataset":
            self.run_git_commands(repository_name, repository_tag)

        if repository_tag == "model":
            set_config_value("version", 1, repository_name)
            self.run_git_commands(repository_name, repository_tag)
            commit_hash = current_commit_hash(repository_name)
            request_payload = {
                    "commit_message" : "Initial commit",
                    "repo" : repository_name,
                    "commit_id":commit_hash,
                    "version":0,
                    "branch":"master"
                }  
            insert_repo_commit(json.dumps(request_payload))
            upload_model_file_list_json(commit_hash, repository_name)

        create_repo_lock(json.dumps({"repo_name":repository_name, "user_name":self.created_by, "locked":False}))
        print("Repository has been created. `cd {}`".format(repository_name))  

        logger.debug(f"END CREATE REPO COMMAND")
    
    def check_git_init(self):
        current_dir = os.getcwd()
        while current_dir != '/':  # Stop when we reach the root directory
            if os.path.exists(os.path.join(current_dir, '.git')):
                return True  # .git folder exists, so project has been initialized
            current_dir = os.path.dirname(current_dir)
        return False

    def clone_repo(self, args):
        if self.check_git_init():
            print("The repo cloning process inside the repository is not possible.")
            sys.exit(50)
        start = timer()
        repository_name = args.name  

        if folder_exists(repository_name):
            print("The repo cloning process could not be completed because the directory already exists.")
            sys.exit(50)

        print('Cloning...')
        run_command_on_subprocess("git clone git@github.com:{0}/{1}.git".format(self.GIT_ORG, repository_name), None, True)    
        tag = get_repository(repository_name)
        if tag == "dataset":
            run_command_on_subprocess("dvc pull", repository_name, True) 
        print("Repository cloned successfully")
        end = timer()
        logger.debug('CLONE TIME {0}'.format(timedelta(seconds=end-start)))    


class CmdRepo(CmdBase):
    def __init__(self, args):
        super().__init__(args)        
        if getattr(self.args, "name", None):
            self.args.name = self.args.name.lower()            
            repo_name_valid(self.args.name)
        else:
            raise RctlValidRequestError("Error: Please provide a valid name, -n")
class CmdRepoCreate(CmdRepo):
    def run(self):   
        log_setup(self.args)  
        repo = RepoMain()        
        if self.args.create:
            repo.create_repo(self.args)
        if self.args.clone:
            repo.clone_repo(self.args)                                    
        return 0


def add_parser(subparsers, parent_parser):
    REPO_HELP = "Create a new repository."
    REPO_DESCRIPTION = (
        "Create a new repository."
    )

    repo_parser = subparsers.add_parser(
        "repo",
        parents=[parent_parser],
        description=REPO_DESCRIPTION,
        help=REPO_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    repo_parser.add_argument(
        "-create",
        "--create",
        action="store_true",
        default=False,
        help="Create new repo",
    )

    repo_parser.add_argument(
        "-clone",
        "--clone",
        action="store_true",
        default=False,
        help="Clone new repo",
    )

    repo_parser.add_argument(
        "-n", 
        "--name", 
        nargs="?", 
        help="Name of the repo",
    )


    repo_parser.add_argument(
        "-tag", 
        "--tag", 
        nargs="?", 
        help="Tag of the repo",
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
    
    repo_parser.set_defaults(func=CmdRepoCreate)
