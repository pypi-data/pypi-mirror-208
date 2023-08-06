import boto3
import re
import os
import time

ATHENA_SQL = 'select localtimestamp'
ATHENA_DEFAULT = {
    'profile': 'YOUR_AWS_PROFILE',
    'region': 'us-east-1',
    'database': 'YOUR_ATHENA_DATABASE',
    'bucket': 'YOUR_S3_BUCKET_FOR_ATHENA',
    'path': 'YOUR_S3_PATH'
}
"""type: dict

Args:
    profile (str): AWS_PROFILE as defined in ~/.aws/config
    region (str): Defaults to *us-east-1*
    database (str): Athena database name
    bucket (str): S3 bucket used for Athena outputs
    path (str): Object path where the results will be stored under.
"""



__desc__ = 'Library for querying AWS Athena'
__modname__ = 'jlibs.aws.athena'

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


def _athena_query(client, query = ATHENA_SQL, params = ATHENA_DEFAULT):
    response = client.start_query_execution(
        QueryString = query,
        QueryExecutionContext={
            'Database': params['database']
        },
         ResultConfiguration={
            'OutputLocation': 's3://' + params['bucket'] + '/' + params['path']
        }
    )
    return response


def _download_from_s3(session, object_key = None, save_as = None, params = ATHENA_DEFAULT):
    s3 = session.client('s3')
    s3.download_file(params['bucket'], params['path'] + '/' + object_key, save_as)


def query(query = ATHENA_SQL, params = ATHENA_DEFAULT, save_as = None, max_execution = 5, verbose = False, download = False):
    """
    Executes an SQL query using Amazon Athena.

    Args:
        query (str): The SQL query to be executed. Defaults to ATHENA_SQL.
        params (dict): The parameters for the query execution. Defaults to ATHENA_DEFAULT.
        save_as (str): The filename to save the query results. If None, the filename is obtained from the S3 path.
        max_execution (int): The maximum number of times to check for query completion. Defaults to 5.
        verbose (bool): If True, displays additional information about the execution and download. Defaults to False.
        download (bool): If True, downloads the query results to the local file system. Defaults to False.

    Returns:
        str: The filename of the query results if successful, False otherwise.
    """
    # Set the session and client to the correct account and region
    session = boto3.Session(profile_name=params['profile'])
    athena = session.client('athena', region_name=params['region'])

    # Execute the SQL query
    execution = _athena_query(athena, query, params)
    query_exec_id = execution['QueryExecutionId']
    state = 'RUNNING'

    # Wait for query completion
    while (max_execution > 0 and state in ['RUNNING', 'QUEUED']):
        max_execution = max_execution - 1
        waiter_response = athena.get_query_execution(QueryExecutionId=query_exec_id)

        if 'QueryExecution' in waiter_response and \
            'Status' in waiter_response['QueryExecution'] and \
            'State' in waiter_response['QueryExecution']['Status']:
                
            state = waiter_response['QueryExecution']['Status']['State']
            if state == 'FAILED':
                return False
            elif state == 'SUCCEEDED':
                s3_path = waiter_response['QueryExecution']['ResultConfiguration']['OutputLocation']
                filename = re.findall(r'.*/(.*)', s3_path)[0]

                if save_as is None:
                    localfile = filename
                else:
                    localfile = save_as
                    download = True

                if verbose:
                    print(f'Stored in S3 as {filename}')

                if download:
                    _download_from_s3(session, filename, localfile)
                    print(f'Downloaded to {localfile}')

                return filename
        time.sleep(1)
    return False




if __name__ == '__main__':
    _hello()