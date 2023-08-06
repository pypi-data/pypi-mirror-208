from __future__ import print_function
import os
import sys
import json
from Accuinsight.modeler.core.LcConst import LcConst

_BASH_RC_PATH = '/home/notebook/.bashrc'


def get_os_env(env_type='LC', env_path=None, env_file=None):
    _ENV_PREFIX = env_type + '_'

    env_value = {}
    if env_path is None:
        env_path = '/usr'
    if env_file is None:
        env_file = '.accu_env'

    env_file = open(env_path + '/' + env_file, 'r')
    while True:
        line = env_file.readline()
        if not line:
            break

        if _ENV_PREFIX in line:
            key, value = line.split('=')
            if key is not None:
                if _ENV_PREFIX in key:
                    value = value.rstrip()
                    env_value.setdefault(key, value)

    return env_value


def is_in_ipython():
    return 'ipykernel_launcher.py' in sys.argv[0]


def get_current_notebook():
    if is_in_ipython():
        target_path = LcConst.ENV_JUPYTER_WORKSPACE
        # '/home/notebook/.jupyter/lab/workspaces'
        if os.path.isdir(target_path):  # if jupyter lab
            file_lists = dict()
            file_name = None
            for (dir_path, dir_names, file_names) in os.walk(target_path):
                for fn in file_names:
                    if not fn.endswith('.swp'):
                        file_lists[fn] = os.path.getmtime(target_path + "/" + fn)
            sorted_file_lists_modified = sorted(file_lists.items(), key=lambda item: item[1], reverse=True)
            file_name = sorted_file_lists_modified[0][0]
            print("Current Jupyter lab meta file: ", file_name)

            with open(target_path + '/' + file_name, 'r') as tf:
                strlines = tf.readlines()
                json_file = json.loads(strlines[0])
                return json_file['data']['layout-restorer:data']['main']['current'].split(':')[1]
        else:
            return "Invalid path."
    else:
        return "Check this file. -> 'ipykernel_launcher.py' with argv[0]"


def get_current_notebook_temp():
    if is_in_ipython():
        print('---------------Path info check---------------')
        print("Relative path from '/home/work/': ", os.path.relpath(os.path.curdir, LcConst.ENV_JUPYTER_HOME_DIR))
        target_path1 = os.path.relpath(os.path.curdir, LcConst.ENV_JUPYTER_HOME_DIR)
        print("Absolute path: ", os.path.abspath(os.path.curdir))
        target_path = os.path.abspath(os.path.curdir)
        print('---------------------------------------------')
        print('---------------------------------------------')
        # target_path = LcConst.ENV_JUPYTER_WORKSPACE
        # '/home/notebook/.jupyter/lab/workspaces'
        if os.path.isdir(target_path):  # if jupyter lab
            file_lists = dict()
            file_name = None
            for (dir_path, dir_names, file_names) in os.walk(target_path + '/.ipynb_checkpoints'):
                for fn in file_names:
                    # print(fn)
                    # print(": ", os.path.getmtime(target_path + '/.ipynb_checkpoints/' + fn))
                    if not fn.endswith('.swp'):
                        file_lists[fn] = os.path.getmtime(target_path + '/.ipynb_checkpoints/' + fn)
            # print(file_lists)
            sorted_file_lists_modified = sorted(file_lists.items(), key=lambda item: item[1], reverse=True)
            # print(sorted_file_lists_modified)
            file_name = sorted_file_lists_modified[0][0]
            # print(file_name)
            # print(target_path + '/' + file_name)
            print("Current working file: ", os.path.relpath(os.path.curdir, LcConst.ENV_JUPYTER_HOME_DIR) + '/' + file_name)
            if (os.path.relpath(os.path.curdir, LcConst.ENV_JUPYTER_HOME_DIR)) == '.':
                return file_name.replace('-checkpoint.ipynb', '.ipynb', -1)
            else:
                return os.path.relpath(os.path.curdir, LcConst.ENV_JUPYTER_HOME_DIR) + '/' + file_name.replace('-checkpoint.ipynb', '.ipynb', -1)
        else:
            return "Invalid path."
    else:
        return "Check this file. -> 'ipykernel_launcher.py' with argv[0]"
