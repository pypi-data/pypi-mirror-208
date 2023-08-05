import copy
import traceback as tb

import pandas as pd
from pydantic import ValidationError
from tabulate import tabulate

from polly_validator.utility.helper import build_field_name_to_original_name_mapping, \
    print_exception, schema_correction, modify_metadata_as_per_mapping
from polly_validator.validators.schema_constructors.dataset_level import build_schema_for_repo


def check_metadata_for_errors(repo, schema_dict, metadata_list, validate_on='value', print_table=False):
    """
    Utility to return errors for a list of dataset level metadata dicts
    Args:
        repo: name of repo
        schema_dict: schema df of the repo
        metadata_list: list of dicts containing the dataset level metadata to be checked
        env:
        auth_token:
        validate_on: level of checks to do, level='schema', 'value'
        print_table: flag to print the results as a table on cli or not

    Returns:
        error_df :  errors as an error df
        status: Status for if the given metadata passed all checks or not as a dict
    """
    try:
        errors_all, status_all = [pd.DataFrame(columns=['Field', 'Error Message', 'Repo',
                                                        'dataset_id', 'Original Name'])], {}
        # Parameter checks:
        if not repo:
            raise Exception('Repo name not entered or is an empty string.')
        if schema_dict is None or schema_dict == {}:
            raise Exception('Schema not entered/empty dictionary passed')
        if metadata_list is None or len(metadata_list) == 0:
            raise Exception('Metadata list is None or is an empty list.')

        metadata_list_copy = copy.deepcopy(metadata_list)
        metadata_list_copy = modify_metadata_as_per_mapping(metadata_list_copy, schema_dict)

        if metadata_list_copy is None:
            raise Exception('Error modifying metadata as per mapping from schema.')
        for index, metadata in enumerate(metadata_list_copy):
            errors, status = validate_dataset_metadata(repo, schema_dict, metadata, validate_on)
            if errors.empty and status is False:
                print(f'Error validating metadata')
            errors_all.append(errors)
            if 'dataset_id' in metadata:
                if not isinstance(metadata['dataset_id'], str):
                    status_all[str(metadata['dataset_id'])] = status
                else:
                    status_all[metadata['dataset_id']] = status
            else:
                status_all[index] = status
        error_df = pd.concat(errors_all, ignore_index=True)

        field_name_mapping = build_field_name_to_original_name_mapping(schema_dict)
        if field_name_mapping is None:
            raise Exception('Error creating field name to original name mapping')
        error_df['Original Name'] = error_df['Field'].apply(
            lambda row: field_name_mapping[row] if row in field_name_mapping
            else 'NA')

        # Reordering columns
        error_df = error_df[['dataset_id',
                             'Field',
                             'Original Name',
                             'Error Message',
                             'Repo']]
        if print_table:
            # 'print_table' is True: returns formatted table for the command line
            print(tabulate(error_df, headers="keys", tablefmt="fancy_grid"))
        del metadata_list_copy
        return error_df, status_all
    except Exception:
        print(tb.format_exc())
        print_exception()
        return pd.DataFrame(), {}


def validate_dataset_metadata(repo, schema_dict, metadata, level='value'):
    """
    Validation per item of dataset metadata
    Args:
        repo:
        schema_dict:
        metadata:
        level:

    Returns:
        collected_errors: errors collected for the single dataset metadata
        status: boolean status for if the dataset metadata passed the checks with no errors or not.
    """
    schema_errors = pd.DataFrame(columns=['Field', 'Error Message', 'Error Type', 'Repo',
                                          'dataset_id', 'key'])
    value_errors = pd.DataFrame(columns=['Field', 'Error Message', 'Error Type', 'Repo',
                                         'dataset_id', 'key'])
    collected_errors = pd.DataFrame(columns=['Field', 'Error Message', 'Error Type', 'Repo',
                                             'dataset_id', 'key'])
    try:
        schema, schema_with_validators = build_schema_for_repo(schema_dict)
        if not schema or not schema_with_validators:
            raise Exception(f'Error building pydantic classes. {tb.format_exc()}')
        if level == 'schema':
            try:
                schema(**metadata)
            except ValidationError as s_errors:
                schema_errors = pd.DataFrame(s_errors.errors())
                # Rename columns to our desired names
            if not schema_errors.empty:
                schema_errors.rename(columns={'loc': 'Field',
                                              'msg': 'Error Message',
                                              'type': 'Error Type'}, inplace=True)
                schema_errors['Repo'] = repo
                if 'dataset_id' in metadata:
                    if isinstance(metadata['dataset_id'], list):
                        schema_errors['dataset_id'] = metadata['dataset_id'][0]
                    else:
                        schema_errors['dataset_id'] = metadata['dataset_id']
                else:
                    schema_errors['dataset_id'] = 'NA'
                if 'key' in metadata:
                    if not isinstance(metadata['key'], str):
                        schema_errors['key'] = str(metadata['key'])
                    else:
                        schema_errors['key'] = metadata['key']
                else:
                    schema_errors['key'] = 'NA'
                schema_errors['Field'] = schema_errors['Field'].apply(lambda row: row[0])
                if 'ctx' in schema_errors.columns:
                    schema_errors.drop(['ctx'], axis=1, inplace=True)
                schema_errors.drop_duplicates(inplace=True)
                return schema_errors, False
            else:
                return collected_errors, True
        elif level == 'value':
            """Step 1. Check only for schema"""
            try:
                schema(**metadata)
            except ValidationError as s_errors:
                schema_errors = pd.DataFrame(s_errors.errors())
                # Rename columns to our desired names
                schema_errors.rename(columns={'loc': 'Field',
                                              'msg': 'Error Message',
                                              'type': 'Error Type'}, inplace=True)
                errors_to_correct = s_errors.errors()
                # Perform intermediate in-memory corrections
                if errors_to_correct:
                    metadata = schema_correction(metadata, errors_to_correct)

            """Step 2. Check for value checks with corrected schema"""
            try:
                schema_with_validators(**metadata)
            except ValidationError as v_errors:
                value_errors = pd.DataFrame(v_errors.errors())
                # Rename columns to our desired names
                value_errors.rename(columns={'loc': 'Field',
                                             'msg': 'Error Message',
                                             'type': 'Error Type'}, inplace=True)
            # If some errors are found in any of the two checks. Concatenate them together.
            collected_errors = pd.concat([schema_errors, value_errors], ignore_index=True)
            if 'ctx' in collected_errors.columns:
                collected_errors.drop(['ctx'], axis=1, inplace=True)
            collected_errors.drop_duplicates(inplace=True)
            collected_errors['Repo'] = repo

            if 'dataset_id' in metadata:
                if not isinstance(metadata['dataset_id'], str):
                    collected_errors['dataset_id'] = str(metadata['dataset_id'])
                else:
                    collected_errors['dataset_id'] = metadata['dataset_id']
            else:
                collected_errors['dataset_id'] = 'NA'

            if 'key' in metadata:
                if not isinstance(metadata['key'], str):
                    collected_errors['key'] = str(metadata['key'])
                else:
                    collected_errors['key'] = metadata['key']
            else:
                collected_errors['key'] = 'NA'
            collected_errors['Field'] = collected_errors['Field'].apply(lambda row: row[0])
            if not collected_errors.empty:
                return collected_errors, False
            else:
                return collected_errors, True
        else:
            raise Exception(f'Invalid value for argument "level": {level} ')
    except Exception as e:
        print(tb.format_exc())
        print_exception()
        return pd.DataFrame(), False