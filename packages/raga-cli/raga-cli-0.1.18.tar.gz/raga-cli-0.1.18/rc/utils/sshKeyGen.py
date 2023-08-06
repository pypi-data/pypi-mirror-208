import logging
import os
from pathlib import Path
import pathlib
import sys
import subprocess

logger = logging.getLogger(__name__)
# Constants
CUR_USER = os.getlogin()
PLATFORM = sys.platform

if PLATFORM == "darwin":
    PRIV_SSH_DIR = "/Users/%s/.ssh" % (CUR_USER)
elif PLATFORM == "linux":
    PRIV_SSH_DIR = "/home/%s/.ssh" % (CUR_USER)


def key_present():    
    if "rc_key.pub" in os.listdir(PRIV_SSH_DIR):
        return True
    else:
        return False
    
def check_git_connection():
    # subprocess.call('ssh -T git@github.com', shell=True)
    logger.debug('SSH key checking on git@github.com')
    result = subprocess.run('ssh -T git@github.com', capture_output=True, shell=True)
    stderr = str(result.stderr, 'UTF-8').lower()
    stdout = str(result.stdout, 'UTF-8').lower()    
    if stderr.find('Permission denied'.lower()) != -1:
        return True    
    if stdout.find('Permission denied'.lower()) != -1:
        return True
    return False

def check_used_key(result):
    stderr = str(result.stderr, 'UTF-8').lower()    
    stdout = str(result.stdout, 'UTF-8').lower()    
    if stderr.find('key is already in use'.lower()) != -1:
        logger.debug('key is already in use')
        return True    
    if stdout.find('key is already in use'.lower()) != -1:
        logger.debug('key is already in use')
        return True
    return False

def gen_ssh_key():   
    owd = os.getcwd()
    os.chdir(PRIV_SSH_DIR)   
    result = subprocess.run('ssh-keygen -t rsa -b 4096 -C "{}@rc" -N "" -f "rc_key"'.format(CUR_USER), capture_output=True, shell=True)     
    stderr = str(result.stderr, 'UTF-8').lower()    
    logger.debug(stderr)
    stdout = str(result.stdout, 'UTF-8').lower()  
    logger.debug(stdout)
    result = subprocess.run('eval "$(ssh-agent -s)"', capture_output=True, shell=True)     
    stderr = str(result.stderr, 'UTF-8').lower()    
    logger.debug(stderr)
    stdout = str(result.stdout, 'UTF-8').lower()  
    logger.debug(stdout)
    result = subprocess.run('ssh-add -K {}/rc_key'.format(PRIV_SSH_DIR), capture_output=True, shell=True)     
    stderr = str(result.stderr, 'UTF-8').lower()    
    logger.debug(stderr)
    stdout = str(result.stdout, 'UTF-8').lower()  
    logger.debug(stdout)
    os.chdir(owd)

def ssh_key_set_up():        
    owd = os.getcwd()
    os.chdir(PRIV_SSH_DIR)
    if check_git_connection():
        if key_present():     
            logger.debug('SSH key adding...')   
            result = subprocess.run('gh ssh-key add {}/rc_key.pub'.format(PRIV_SSH_DIR), capture_output=True, shell=True)     
            print(check_used_key(result))
        else:       
            logger.debug('SSH key generating...')  
            gen_ssh_key()
            logger.debug('SSH key adding...')   
            subprocess.run('gh ssh-key add {}/rc_key.pub'.format(PRIV_SSH_DIR),capture_output=True, shell=True)        
    os.chdir(owd)
