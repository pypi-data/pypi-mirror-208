import base64
import json
import os
import sys
import traceback as tb
from datetime import datetime as dt
from functools import wraps

import requests as rq
from pydantic import StrictFloat, StrictInt, StrictStr, conlist, create_model

DATATYPE_MAP = {'text': StrictStr,
                'integer': StrictInt,
                'float': StrictFloat,
                'object': dict,
                'boolean': bool}


def build_original_name_to_field_name_mapping(schema_dict):
    """
    Given a schema dict for a repo, create a mapping for original name vs representative name
    Args:
        schema_dict:

    Returns:

    """
    res = {}
    for k, v in schema_dict.items():
        res[v['original_name']] = k
    return res


def build_field_name_to_original_name_mapping(schema_dict):
    """
    Given a schema dict for a repo, create a mapping for representative name vs original name
    Args:
        schema_dict:

    Returns:

    """
    try:
        res = {}
        for k, v in schema_dict.items():
            res[k] = v['original_name']
        return res
    except Exception:
        print(tb.format_exc())
        print_exception()
        return None


def modify_metadata_as_per_mapping(metadata_list, schema_dict):
    """
    Given a metadata list, repo and schema level. Perform the following steps:
    1. Create mapping for original name vs the representative name
    2. Change the key names in the metadata list to representative names.
    Args:
        schema_dict:
        metadata_list:

    Returns:

    """
    try:
        # Step 1
        orig_name_mapping = build_original_name_to_field_name_mapping(schema_dict)
        # Step 2
        for metadata in metadata_list:
            for k, v in orig_name_mapping.items():
                if k in metadata and k != v:
                    metadata[v] = metadata.pop(k)
        return metadata_list
    except Exception:
        print(tb.format_exc())
        print_exception()
        return None


def timeit(func):
    """
    Timing function to time error collection.
    Args:
        func:

    Returns:
    """

    @wraps(func)
    def timed(*args, **kw):
        tstart = dt.now()
        output = func(*args, **kw)
        tend = dt.now()
        print('"{}" took {} to execute.\n'.format(func.__name__, (tend - tstart)))
        return output

    return timed


def list_to_set_in_dict(obj):
    """
    Recursively convert list values inside a dic to sets
    Args:
        obj: Current value being checked

    Returns:
        obj: Dict with lists converted to sets.
    """
    if isinstance(obj, list):
        return {list_to_set_in_dict(v) for v in obj}
    elif isinstance(obj, dict):
        return {k: list_to_set_in_dict(v) for k, v in obj.items()}
    return obj


def lower_and_strip(obj):
    """
    Lower and strip all values in a list
    Args:
        obj:

    Returns:

    """
    for key, val in obj.items():
        if isinstance(val, list) or isinstance(val, set):
            obj[key] = [v.lower().strip() for v in val]
        elif isinstance(val, dict):
            obj[key] = lower_and_strip(obj[key])
    return obj


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def build_validation_schema(schema_dict, for_level, validators=None):
    """
    Takes a description DF and returns a pydantic class with the values taken from the schema
    Args:
        for_level:
        validators:
        schema_dict:

    Returns:

    """
    try:
        if for_level == 'sample':
            schema_dict = {k: v for (k, v) in schema_dict.items() if k.startswith('curated')}
        elif for_level == 'dataset':
            pass
        else:
            raise Exception(f'Invalid argument given for argument "for_level": {for_level}')
        validation_schema_dict = {}
        for field_name, details in schema_dict.items():
            data_type = DATATYPE_MAP[details['type']]
            is_array = details['is_array']
            validation_schema_dict[field_name] = (data_type if not is_array else conlist(data_type, min_items=1), ...)
        if validators is not None:
            schema = create_model('SchemaWithValidators', **validation_schema_dict, __validators__=validators)
        else:
            schema = create_model('Schema', **validation_schema_dict)
        return schema
    except Exception as e:
        print(tb.format_exc())
        print_exception()
        return None


def split_curated_ontological_fields_by_type(ontological_fields, schema_dict):
    """
    Given a list of ontological fields, split them into str fields or list type fields as per description dataframe
    Args:
        schema_dict:
        ontological_fields:
    Returns:

    """
    schema_dict = {k: v for k, v in schema_dict.items() if k.startswith('curated') and k in ontological_fields}
    list_fields = []
    str_fields = []

    for field_name, details in schema_dict.items():
        data_type = details['type']
        is_array = details['is_array']
        if data_type == 'text':
            if is_array:
                list_fields.append(field_name)
            elif not is_array:
                str_fields.append(field_name)
    return str_fields, list_fields


def split_fields_by_type(schema_dict):
    """
    Given a list of ontological fields, split them into str fields or list type fields as per description dataframe
    Args:
        schema_dict:

    Returns:

    """
    list_fields = []
    str_fields = []
    for field_name, details in schema_dict.items():
        data_type = details['type']
        is_array = details['is_array']
        if data_type == 'text':
            if is_array:
                list_fields.append(field_name)
            elif not is_array:
                str_fields.append(field_name)
    return str_fields, list_fields


def split_curated_fields_by_type(curated_fields, schema_dict):
    """
    Given a list of ontological fields, split them into str fields or list type fields as per description dataframe
    Args:
        curated_fields:
        schema_dict:

    Returns:

    """
    list_fields = []
    str_fields = []
    for field_name, details in schema_dict.items():
        data_type = details['type']
        is_array = details['is_array']
        if field_name in curated_fields and data_type == 'text':
            if is_array:
                list_fields.append(field_name)
            elif not is_array:
                str_fields.append(field_name)
    return str_fields, list_fields


def schema_correction(meta, err):
    """
    Type Modification:
        - If errors are found, collect the errors and perform in-memory modifications of the metadata values.
        This correction can be one of the following:
            If the value should be a list but the incoming value is a string, typecast it into a list
            E.g. ‘Cancer’ will be changed to ['Cancer']

            If the value should be a string, but the incoming value is an integer, typecast it into a string.
            E.g. 2021 will change to ‘2021’.
        - If no errors are found, perform no in-memory modifications.
    Args:
        meta: sample level metadata dict
        err: list of dict of schema errors

    Returns:

    """
    for e in err:
        field = e['loc'][0]
        if e['type'] == 'type_error.list':
            meta[field] = [meta[field]]
        elif e['type'] == 'type_error.str':
            meta[field] = str(meta[field])
    return meta


def print_exception():
    """
    Print exception in detail
    Returns:

    """
    exception_type, exception_object, exception_traceback = sys.exc_info()
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno
    print("Exception type: ", exception_type)
    print("File name: ", filename)
    print("Line number: ", line_number)


def get_data_types_data_sources():
    """Getting Data Type and Data Source values from a separate repo on GitHub"""
    try:
        response_data_types = rq.get(f'https://raw.githubusercontent.com/ElucidataInc/PublicAssets/'
                                     f'master/polly_validator/accepted_data_types.txt')
        if response_data_types.status_code != 200:
            raise Exception(f"Unable to retrieve data type file from GitHub. Status Code: "
                            f"{response_data_types.status_code}")
        valid_data_types = base64.b64decode(response_data_types.content).decode('ascii').split('\n')
        print(f'Retrieved Valid Data Types')

        response_data_sources = rq.get(f'https://raw.githubusercontent.com/ElucidataInc/PublicAssets/'
                                       f'master/polly_validator/accepted_data_sources.txt')
        if response_data_sources.status_code != 200:
            raise Exception(f"Unable to retrieve data source file from GitHub. Status Code: "
                            f"{response_data_sources.status_code}")
        valid_data_sources = base64.b64decode(response_data_sources.content).decode('ascii').split('\n')
        print(f'Retrieved Valid Data Sources')
        return valid_data_types, valid_data_sources
    except Exception as e:
        print(tb.format_exc())
        print_exception()
        return [], []
