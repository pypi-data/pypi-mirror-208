from datetime import timedelta
import logging
import threading
import time

from rc.cli.utils import compare_dot_dvc_file, run_command_on_subprocess
from timeit import default_timer as timer
from rc.cli.utils import *
from rc.utils.config import set_config_value
from rc.utils.folder_file import check_empty_dirs, check_root_folder
from rc.utils.request import get_commit_version, is_repo_lock, update_repo_commit_id, update_repo_lock, insert_repo_commit, get_repository

logger = logging.getLogger(__name__)
repo_commit_ids = []
pool_time = 10
#Create an Event object
stop_event = threading.Event()

def dir_add(path):
    start = timer()
    if compare_dot_dvc_file(path):
        run_command_on_subprocess("dvc commit {0} -f".format(path))
    else:
        run_command_on_subprocess("dvc add {0}".format(path))
    run_command_on_subprocess("git add {0}.dvc".format(path))
    logger.debug('DVC ADD TIME {0}'.format(timedelta(seconds=timer()-start)))

def dir_upload(paths):
    start = timer()
    run_command_on_subprocess("dvc push {0}".format(' '.join(paths)))
    logger.debug('DVC PUSH TIME {0}'.format(timedelta(seconds=timer()-start)))   

@retry(Exception, tries=4, delay=3, backoff=2)
def dataset_upload(paths,message,repo,current_version):
    if not is_current_version_stable():
        return False   
    
    paths = back_slash_trim(paths)

    for path in paths:
        dir_add(path)
    
    if not check_git_add_untrack_files() and not check_git_commit_files():
        print("There are no changes since last update.")
        return False
    
    dir_upload(paths)
    for path in paths:     
        md5_dir = get_dir_file(path)          
        request_payload = {
            "folder": path,
            "commit_message" : message,
            "repo" : repo,
            "dir_file":md5_dir,
            "version":current_version,
            "commit_id":"",
        }   
        commit_id = insert_repo_commit(json.dumps(request_payload))
        repo_commit_ids.append(commit_id['id'])
        logger.debug("Data upload for {}".format(path))
        set_config_value("version", current_version)
    
    stop_checking_elastic_process = False
    while not stop_checking_elastic_process:
        stop_checking_elastic_process = server_repo_commit_status(repo_commit_ids)
        if not stop_checking_elastic_process:
            time.sleep(pool_time)
    return True

def model_upload(message, repo, model_version):
    if check_git_add_untrack_files():
        print('Untracked files present. Push new files to repository to save.')
        sys.exit()
    if check_git_commit_files():
        print('Untracked files present. Push new files to repository to save.')
        sys.exit()
    if check_push_left():
        print('Untracked files present. Push new files to repository to save.')
        sys.exit()
    if check_git_deleted_files():
        print('Untracked files present. Push new files to repository to save.')
        sys.exit()
    commit_hash = current_commit_hash()
    if get_commit_version(commit_hash):
        print("There are no changes since last update.")
        sys.exit(50)
    branchName = current_branch()
    request_payload = {
                "commit_message" : message,
                "repo" : repo,
                "commit_id":commit_hash,
                "version":model_version,
                "branch":branchName
            }  
    upload_model_file_list_json(commit_hash)
    # upload_inferences_json(model_version)
    insert_repo_commit(json.dumps(request_payload))
    logger.debug("Data upload for branch {0} and {1} ".format(branchName,commit_hash ))
    

def make_repo_lock(stop_event):
    logger.debug("START HTTP THREAD")
    repo = get_repo() 
    while not stop_event.is_set():
        logger.debug("REPO LOCKING")
        update_repo_lock(repo, json.dumps({"locked":True}))
        time.sleep(pool_time)

def make_repo_commit(message):
    if len(repo_commit_ids):
        run_command_on_subprocess("git commit -m '{}' -a".format(message), None, True)
        run_command_on_subprocess("git push", None, True)
        for id in repo_commit_ids:     
            commit_hash = current_commit_hash()
            request_payload = {
                "id" : id,
                "commit_id":commit_hash,
            }   
            update_repo_commit_id(json.dumps(request_payload))
            logger.debug("Data committed")
    else:
        logger.debug("Repo IDs not found.")
        print("Server not responding")
        sys.exit()
    

def put(args):
    from rc.utils.folder_file import get_non_empty_folders
    start = timer()
    message = args.message      
    repo = get_repo()     

    tag = get_repository(repo)
    is_repo_lock(repo)
    
    if tag == "dataset":
        if check_root_folder():
            print("File should not be present directly in the root folder of a dataset.")
            sys.exit()
        print("Files uploading...")   
        paths = get_non_empty_folders(args.path) 
        if not paths:
            print("Either the directory is empty or there are no directories in the repository.")
            sys.exit()
        current_version = dataset_current_version(paths, repo)
        # Create a thread for making an HTTP request
        http_thread = threading.Thread(target=make_repo_lock, args=(stop_event,))
        http_thread.start() 
        try:
            if dataset_upload(paths,message,repo, current_version):
                # Set the stop event
                stop_event.set()
                update_repo_lock(repo, json.dumps({"locked":False}))
                upload_dataset(repo, current_version)
                make_repo_commit(message)
            else:
                # Set the stop event
                stop_event.set()
                update_repo_lock(repo, json.dumps({"locked":False}))
                # Wait for both threads to finish
                http_thread.join()
                sys.exit()
        except Exception as e:
            # Set the stop event
            stop_event.set()
            update_repo_lock(repo, json.dumps({"locked":False}))
            print("Something went wrong.")
            logger.exception(e)
            # Wait for both threads to finish
            http_thread.join()
            sys.exit()
        # Start both threads
        print("Files uploaded successfully")
    elif tag == "model":
        print("Model files uploading...")
        if check_empty_dirs(os.getcwd()):
            print("Empty directory found.")
        model_version = model_current_version(repo)
        check_extensions()
        # set_config_value("version", model_version)
        model_upload(message, repo, model_version)
        upload_model(repo, model_version)
        upload_inferences_ingest(repo, model_version)
        print("Model files uploaded successfully")
    
    update_repo_lock(repo, json.dumps({"locked":False}))
    logger.debug('TOTAL UPLOAD TIME {0}'.format(timedelta(seconds=timer()-start)))