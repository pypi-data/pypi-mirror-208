import os
import time
import pickle

CACHE_FILE_DEFAULT = "jlibs.cache"
CACHE_TIME_DEFAULT = 1 * 60 * 60  # 1 hour in seconds


__desc__ = 'Library for caching expirable data to reduce subsequent calls'
__modname__ = 'jlibs.file.cache'

def hi():
    """
    Prints simple a greeting message used for testing
    """
    print(f"Hello from \033[33m{__modname__}\033[0m module")
    return __modname__


def _hello():
    release = time.strftime('%Y.%m.%d', time.localtime(os.path.getmtime(__file__)))
    print(f"\nModule : \033[34m{__modname__}\033[0m")
    print(f"Release: \033[34m{release}\033[0m")
    print(f"\033[35m{__desc__}\033[0m")
    print(f"\nThis is part of the JLIBS package (\033[32mhttps://pypi.org/project/jlibs/\033[0m)")
    print(f"Created by John Anthony Mariquit (john@mariquit.com)")
    return __modname__


def load(cache_file = CACHE_FILE_DEFAULT, cache_time = CACHE_TIME_DEFAULT, verbose = False):
    cache_data = []

    # check if cache_file exists and is not older than cache_time
    if os.path.exists(cache_file):
        file_time = os.path.getmtime(cache_file)
        if time.time() - file_time < cache_time:
            # load cached results from file
            if verbose:
                print(f"Loading from {cache_file}")
            with open(cache_file, "rb") as f:
                cache_data = pickle.load(f)
        else:
            if verbose:
                print(f"Stale cache in {cache_file}")
    
    return cache_data

def save(cache_data, cache_file = CACHE_FILE_DEFAULT, verbose = False):
    with open(cache_file, "wb") as f:
        pickle.dump(cache_data, f)
    if verbose:
        print(f"Saved to {cache_file}")




if __name__ == '__main__':
    _hello()
