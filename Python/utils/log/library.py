import os
from datetime import datetime

from utils.log.subscriptions import g_on_log


def store_to_file(fpath, data):
    os.makedirs(fpath, exist_ok=True)
    with open(fpath, 'w') as f:
        f.write(data)

def log_fname(postfix=''):
    return f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}{postfix}.log"

def store(data, prefix=''):
    store_to_file(prefix + log_fname(), data)

def redirect_to_file(fpath=None):
    _fpath = fpath or f"logs/{log_fname()}"
    os.makedirs(os.path.dirname(_fpath), exist_ok=True)
    file = open(_fpath, "a")
    def on_log(log):
        full_message, message, level, title, time = log
        file.write(f"{full_message}\n")
        file.flush()
    g_on_log.subscribe(on_log, file)
    return file