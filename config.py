import copy
import os
import json
import codecs

ROOT_FOLDER = os.path.dirname(__file__)

PID_PATH = os.path.join(ROOT_FOLDER, 'server.pid')
CONFIG_PATH = os.path.join(ROOT_FOLDER, 'config.json')

DEFAULT_CONFIG = {
    'LAUNCH_LIST': [],
}


def get_config():
    if not os.path.exists(CONFIG_PATH):
        with codecs.open(CONFIG_PATH, 'wb', encoding='utf-8') as f:
            f.write(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=4))
        return copy.deepcopy(DEFAULT_CONFIG)
    else:
        with codecs.open(CONFIG_PATH, 'rb', encoding='utf-8') as f:
            return json.load(f)


def save_pid(pid):
    with codecs.open(PID_PATH, 'ab', 'utf-8') as f:
        f.write(str(pid) + os.linesep)


def clear_pid():
    with codecs.open(PID_PATH, 'wb', 'utf-8') as f:
        f.write('')
