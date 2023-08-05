import json
import os
import pathlib

from polly_validator.config import CONFIG

ROOT = pathlib.Path(__file__).parent.parent


def create_job_json():
    """
    Construct a job.json file whilst taking credentials from the ~/.aws/credentials file and AUTH_TOKEN for polly-py
    Returns:

    """
    job_json = CONFIG['repo_wise_run_config']['job_details']
    creds = {}
    # if 'AUTH_KEY' in os.environ:
    #     creds['AUTH_KEY'] = os.environ['AUTH_KEY']
    # job_json['secret_env'] = creds

    with open(ROOT / 'job.json', 'w') as fp:
        json.dump(job_json, fp, indent=4)


if __name__ == '__main__':
    create_job_json()
