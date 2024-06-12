import os
import sys
import time

import config
import subprocess

save_pid = config.save_pid
clear_pid = config.clear_pid
get_config = config.get_config
ROOT_FOLDER = config.ROOT_FOLDER

process_list = []
config_data = get_config()
LAUNCH_LIST = config_data['LAUNCH_LIST']

if __name__ == '__main__':
    clear_pid()
    if len(LAUNCH_LIST) == 0:
        raise Exception('config.json 中 LAUNCH_LIST 列表为空')

    save_pid(os.getpid())

    for launch_item in LAUNCH_LIST:
        launch_path = os.path.join(ROOT_FOLDER, launch_item)
        if not os.path.exists(launch_path):
            print(f'Launch Path 不存在: {launch_path}')
            continue
        if not launch_item.endswith('py'):
            print(f'Launch Path 不符合要求: {launch_path}')
            continue
        process = subprocess.Popen([sys.executable, launch_path],
                                   stdout=sys.stdout,
                                   stderr=sys.stderr,
                                   shell=False)
        process_list.append(process)
        save_pid(process.pid)
        print(f'子进程 {launch_item} 已启动')

    while True:
        time.sleep(60 * 60 * 24)
