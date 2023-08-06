import os
import pwd
import json
import getpass
from .identity import Identity

def empty(data: str):
    if (data is None) or (len(data) == 0):
        return True
    return False


def get_system_user():
    try:
        user = pwd.getpwuid(os.getuid())[0]
    except:
        user = os.environ.get('NB_USER', getpass.getuser())
    return user


def get_user_home_path():
    username = get_system_user()
    if username is None:
        return None

    pathDir = f"/home/{username}"
    try:
        with Identity(username):
            pathDir = os.path.expanduser(
                f"~{pwd.getpwuid(os.geteuid())[0]}")
    except:
        pass

    return pathDir

def get_user_study_root_path():
    return f"{get_user_home_path()}/studies"

def get_user_notebook_root_path():
    return f"{get_user_home_path()}/notebooks"

def get_user_app_root_path():
    return f"{get_user_home_path()}/apps"

def get_settings():
    obj = {}
    user_home_path = get_user_home_path()
    if user_home_path is None:
        return obj

    bio_key_file = f"{user_home_path}/.bioapi.key"
    if os.path.exists(bio_key_file):
        with open(bio_key_file) as f:
            try:
                obj = json.loads(f.read().strip())
            except:
                pass
            f.close()

    return obj
