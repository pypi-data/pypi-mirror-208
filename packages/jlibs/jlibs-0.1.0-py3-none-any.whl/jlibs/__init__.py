
__all__ = ['csv', 'cache', 'ec2', 'accounts', 'athena']

if __name__ == '__main__':
    import os
    import time
    modules = ', '.join(__all__)
    version = time.strftime('%Y.%m.%d', time.localtime(os.path.getmtime(__file__)))

    print(f"Package : \033[36mJLIBS\033[0m")
    print(f"Author  : \033[36mJohn Anthony Mariquit\033[0m (john@mariquit.com)")
    print(f"Modules : \033[34m{modules}\033[0m")
    print(f"Release : \033[34m{version}\033[0m")

if __name__ != '__main__':
    from .file import csv, cache
    from .aws import ec2, accounts, athena
