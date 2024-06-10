import os
from datetime import datetime


def store_to_file( fpath, data ):
    os.makedirs( fpath, exist_ok=True)
    with open( fpath, 'w' ) as f:
        f.write( data )

def log_fname( postfix='' ):
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + postfix + '.log'

def store( data, prefix='' ):
    store_to_file( prefix + log_fname(), data )