import os
import time


__desc__ = 'Library for retrieving AWS accounts'
__modname__ = 'jlibs.aws.accounts'

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




if __name__ == '__main__':
    _hello()