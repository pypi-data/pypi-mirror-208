import gc
import os
import traceback as tb
from collections import defaultdict
from datetime import datetime as dt
from multiprocessing import Pool

import pandas as pd
import psutil
from polly_validator.utility.helper import chunks, print_exception
from polly_validator.validators import dataset_metadata_validator
from polly_validator.validators import sample_metadata_validator
from polly_validator.settings import REPOS_FOR_DATASET_LEVEL_VALIDATION, REPOS_FOR_SAMPLE_LEVEL_VALIDATION, \
    RUN_DATASET_LEVEL_VALIDATIONS, RUN_SAMPLE_LEVEL_VALIDATIONS, \
    DATASET_ERRORS_TABLE, SAMPLE_ERRORS_TABLE, \
    DB_NAME, \
    SCHEMAS_FOR_DATASET_LEVEL_VALIDATION, SCHEMAS_FOR_SAMPLE_LEVEL_VALIDATION, \
    DATASET_ID_LIST, \
    DATASET_LEVEL_ERROR_COLLECTION_CHUNK_SIZE, SAMPLE_LEVEL_ERROR_COLLECTION_CHUNK_SIZE, \
    SAMPLE_METADATA_QUERY_CHUNK_SIZE
from polly.auth import Polly
from polly.omixatlas import OmixAtlas
from sqlalchemy import create_engine
from tqdm import tqdm

# Obtain authentication tokens
try:
    if 'AUTH_KEY' in os.environ:
        AUTH_KEY = os.environ['AUTH_KEY']
        Polly.auth(AUTH_KEY)
    else:
        raise Exception(f'Polly-python authentication token missing.')
except Exception as e:
    print(tb.format_exc())
    print_exception()

# Defining OMIXATLAS object
OMIXATLAS = OmixAtlas()

dataset_id_list = DATASET_ID_LIST


def get_query_results(query):
    """
    Given a query for Polly-python, return the resultant DF
    Args:
        query: SQL Query

    Returns:
        DataFrame: Response to the query
    """
    return OMIXATLAS.query_metadata(query, query_api_version="v2")


"""----Functions for repo-wise dataset level metadata validation----"""


def dataset_metadata_validator_construct_args_for_pool(repos):
    """
    Function to create arguments for pool of workers to run
    Args:
        repos:

    Returns:

    """
    args_for_pool = defaultdict(list)
    for repo in repos:
        print(f'Using provided schema for: {repo}')
        schema_dict = SCHEMAS_FOR_DATASET_LEVEL_VALIDATION[repo]
        print(f'Getting dataset level metadata for: {repo}')
        t_start = dt.now()
        dataset_metadatas = get_query_results(f"SELECT * FROM {repo}.datasets")
        print(f'Actual time taken to run the query: {dt.now() - t_start}')

        for val in dataset_metadatas.to_dict('records'):
            args_for_pool[repo].append((repo, schema_dict, val))
    return args_for_pool


def check_datasets_metadata_in_repo_for_errors(repos):
    """

    Args:
        repo:

    Returns:

    """
    compiled_error_df = pd.DataFrame(columns=['Field', 'Error Message', 'Error Type', 'Repo',
                                              'dataset_id', 'key'])
    try:
        num_repos = len(repos)
        args_for_pool = dataset_metadata_validator_construct_args_for_pool(repos)
        print(f'RAM Usage: {psutil.virtual_memory().percent}%')
        ctr = 1
        print(f'Compiling errors...')
        print(f'\nWill use {psutil.cpu_count(logical=False)} cores at my disposal...\n')
        chunk_size = DATASET_LEVEL_ERROR_COLLECTION_CHUNK_SIZE
        for repo in repos:
            chunk_no = 1
            print(f'Working on repo: {repo} | Count: {ctr}/{num_repos}')
            total_chunks = len(args_for_pool[repo]) // chunk_size
            tstart = dt.now()
            for args in chunks(args_for_pool[repo], chunk_size):
                print(f'Chunk: {chunk_no}/{total_chunks}')
                process_pool = Pool(processes=psutil.cpu_count(logical=False))
                error_df_results = process_pool.starmap(dataset_metadata_validator.validate_dataset_metadata,
                                                        tqdm(args, total=len(args)))

                # error_df_results = pd.concat(error_df_results, ignore_index=True)
                error_dfs = [res[0] for res in error_df_results]
                compiled_error_df = pd.concat([compiled_error_df, pd.concat(error_dfs, ignore_index=True)],
                                              ignore_index=True)
                del error_df_results, error_dfs
                gc.collect()
                chunk_no += 1
                print(f'RAM Usage: {psutil.virtual_memory().percent}%')
            print(f'Time Taken: {dt.now() - tstart}\n')
            ctr += 1
        compiled_error_df.reset_index(inplace=True, drop=True)
        print(f'RAM Usage: {psutil.virtual_memory().percent}%')
        return compiled_error_df
    except Exception as err:
        print(f'Error when collecting errors: {tb.format_exc()}')
        print_exception()
    return pd.DataFrame(columns=['Field', 'Error Message', 'Error Type', 'Repo',
                                 'dataset_id', 'key'])


"""----Functions for repo-wise sample level metadata validation----"""


def get_samples_for_dataset_id(ds_id):
    matched_samples = get_query_results(
        f"SELECT * FROM sc_data_lake.samples_singlecell where src_dataset_id = '{ds_id}'")
    return matched_samples


def sample_metadata_validator_construct_args_for_pool(repos):
    """

    Args:
        repos:

    Returns:

    """
    args_for_pool = defaultdict(list)
    for repo in repos:
        print(f'Using provided schema for: {repo}')
        schema_dict = SCHEMAS_FOR_SAMPLE_LEVEL_VALIDATION[repo]
        print(f'Getting samples for: {repo}')
        t_start = dt.now()
        """Code for getting all samples."""
        all_samples_df = []
        for chunk in chunks(dataset_id_list, SAMPLE_METADATA_QUERY_CHUNK_SIZE):
            if repo == 'sc_data_lake' or 'single_cell_rnaseq_omixatlas':
                matched_samples = get_query_results(
                    f"SELECT * FROM {repo}.samples_singlecell where src_dataset_id in {*chunk,}")
            else:
                matched_samples = get_query_results(
                    f"SELECT * FROM {repo}.samples where src_dataset_id in {*chunk,}")
            all_samples_df.append(matched_samples)
            print(f'{len(matched_samples)} more samples collected and concatenated.')
        samples = pd.concat(all_samples_df, ignore_index=True)
        print(f'Total {len(samples)} Samples collected.')
        print(f'Actual time taken to collect all samples: {dt.now() - t_start}')

        for val in samples.to_dict('records'):
            args_for_pool[repo].append((repo, schema_dict, val))
    return args_for_pool


def check_samples_metadata_in_repo_for_errors(repos):
    """
    Given a list of repos, go repo by repo and collect errors
    Args:
        repos:list of repos

    Returns:
        pandas DataFrame: containing the errors collected from all the repos
    """
    compiled_error_df = pd.DataFrame(columns=['Field', 'Error Message', 'Error Type', 'Repo',
                                              'src_dataset_id', 'data_id', 'sample_id'])
    try:
        num_repos = len(repos)
        args_for_pool = sample_metadata_validator_construct_args_for_pool(repos)
        print(f'RAM Usage: {psutil.virtual_memory().percent}%')
        ctr = 1
        print(f'Compiling errors...')
        print(f'\nWill use {psutil.cpu_count(logical=False)} cores at my disposal...\n')
        chunk_size = SAMPLE_LEVEL_ERROR_COLLECTION_CHUNK_SIZE
        for repo in repos:
            chunk_no = 1
            print(f'Working on repo: {repo} | Count: {ctr}/{num_repos}')
            total_chunks = len(args_for_pool[repo]) // chunk_size
            tstart = dt.now()
            for args in chunks(args_for_pool[repo], chunk_size):
                print(f'Chunk: {chunk_no}/{total_chunks}')
                process_pool = Pool(processes=psutil.cpu_count(logical=False))
                error_df_results = process_pool.starmap(sample_metadata_validator.validate_sample_metadata,
                                                        tqdm(args, total=len(args)))
                # error_df_results = pd.concat(error_df_results, ignore_index=True)
                error_dfs = [res[0] for res in error_df_results]
                compiled_error_df = pd.concat([compiled_error_df, pd.concat(error_dfs, ignore_index=True)],
                                              ignore_index=True)
                del error_df_results, error_dfs
                gc.collect()
                chunk_no += 1
                print(f'RAM Usage: {psutil.virtual_memory().percent}%')
            print(f'Time Taken: {dt.now() - tstart}\n')
            ctr += 1
        compiled_error_df.reset_index(inplace=True, drop=True)
        print(f'RAM Usage: {psutil.virtual_memory().percent}%')
        return compiled_error_df
    except Exception as err:
        print(f'Error when collecting errors: {tb.format_exc()}')
        print_exception()
    return pd.DataFrame(columns=['Field', 'Error Message', 'Error Type', 'Repo',
                                 'src_dataset_id', 'data_id', 'sample_id'])


if __name__ == '__main__':
    # Run the error collection routine
    try:
        # Initialize DB connection and connect
        engine = create_engine(f'sqlite:///polly_validator/{DB_NAME}')
        # Create an SQLAlchemy connection tob an SQLite object with name: DB_NAME
        conn = engine.connect()
        if RUN_DATASET_LEVEL_VALIDATIONS:
            """Running Dataset Level Error Collection"""
            print(f'\nCollecting errors in dataset metadata from repos: {REPOS_FOR_DATASET_LEVEL_VALIDATION}')
            # Get the compiled error table.
            compiled_dataset_level_errors_df = check_datasets_metadata_in_repo_for_errors(REPOS_FOR_DATASET_LEVEL_VALIDATION)
            if not compiled_dataset_level_errors_df.empty:
                # If the DB exists, append to the table.
                compiled_dataset_level_errors_df = compiled_dataset_level_errors_df.astype(str)
                compiled_dataset_level_errors_df.to_sql(DATASET_ERRORS_TABLE, conn, if_exists='replace', chunksize=1000)
                print(f'\nErrors added to table: {DATASET_ERRORS_TABLE}\nDB: {DB_NAME}\n')
            else:
                print(f'Empty Errors Table Compiled.')

        if RUN_SAMPLE_LEVEL_VALIDATIONS:
            """Running Sample Level Error Collection"""
            print(f'\nCollecting errors in sample metadata from repos: {REPOS_FOR_SAMPLE_LEVEL_VALIDATION}')
            compiled_sample_level_errors_df = check_samples_metadata_in_repo_for_errors(REPOS_FOR_SAMPLE_LEVEL_VALIDATION)
            if not compiled_sample_level_errors_df.empty:
                # If the table exists, append to the table.
                compiled_sample_level_errors_df = compiled_sample_level_errors_df.astype(str)
                compiled_sample_level_errors_df.to_sql(SAMPLE_ERRORS_TABLE, conn, if_exists='replace', chunksize=1000)
                print(f'\nErrors added to table: {SAMPLE_ERRORS_TABLE}\nDB: {DB_NAME}\n')
            else:
                print(f'Empty Errors Table Compiled.')

        # Close the DB connection
        conn.close()
    except Exception as e:
        print(tb.format_exc())
        print_exception()
