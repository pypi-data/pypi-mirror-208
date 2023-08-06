import os
import time
import csv

CSV_NAME_DEFAULT = "jlibs"  # filename without the .csv extension


__desc__ = 'Library for exporting lists to CSV format'
__modname__ = 'jlibs.file.csv'

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


def save(fields = None, rows = None, csv_name = CSV_NAME_DEFAULT, verbose = False):
    # Get the current date and time as a string
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())

    # Write the results to a CSV file with a timestamp suffix
    filename = f"{csv_name}_{timestamp}.csv"

    # replaced code below because ChatGPT said the other code was more efficient
    # with open(filename, 'w', newline='') as csvfile:
    #     fieldnames = ['Account', 'Region', 'InstanceId', 'AMI', 'AMIstate']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #     writer.writeheader()
    #     for result in results:
    #         writer.writerow(result)
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(fields)
        writer.writerows(rows)
        if verbose:
            total = len(rows)
            print(f"Saved {total} lines(s) to {filename}")




if __name__ == '__main__':
    _hello()
