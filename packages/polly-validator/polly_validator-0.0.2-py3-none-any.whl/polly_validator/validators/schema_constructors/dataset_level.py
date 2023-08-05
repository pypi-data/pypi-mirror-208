import copy
import traceback as tb
from datetime import datetime as dt

import rapidfuzz as rf
from pydantic import validator

from polly_validator.settings import FIELD_MAPPING, VALID_NAMES
from polly_validator.utility.helper import build_validation_schema, list_to_set_in_dict, lower_and_strip, \
    print_exception, split_fields_by_type, split_curated_ontological_fields_by_type

# Creating valid name but lowered and stripped
VALID_NAMES_LOWERED = copy.deepcopy(VALID_NAMES)
VALID_NAMES_LOWERED = lower_and_strip(VALID_NAMES_LOWERED)

# Convert all lists to set for faster lookups
VALID_NAMES = list_to_set_in_dict(VALID_NAMES)
VALID_NAMES_LOWERED = list_to_set_in_dict(VALID_NAMES_LOWERED)

ontological_fields = ['curated_disease',
                      'curated_tissue',
                      'curated_organism',
                      'curated_cell_line',
                      'curated_cell_type',
                      'curated_drug']
default_values = ['None', 'Normal']

"""Ontology Check Function"""


def check_ontology(field_to_check, name):
    if field_to_check == 'curated_cell_line':
        # Specifically for kw_cell_line, valid names are stores separately.
        valid = VALID_NAMES[FIELD_MAPPING[field_to_check]]['valid_cell_line_names']
        valid_lowered_stripped = VALID_NAMES_LOWERED[FIELD_MAPPING[field_to_check]]['valid_cell_line_names']
    else:
        valid = VALID_NAMES[FIELD_MAPPING[field_to_check]]
        valid_lowered_stripped = VALID_NAMES_LOWERED[FIELD_MAPPING[field_to_check]]
    if name not in valid and name not in default_values:
        if name.lower().strip() in valid_lowered_stripped:
            possible_match = rf.process.extract(name, valid, scorer=rf.fuzz.ratio, limit=1)[0][0]
            raise ValueError(f'Ontological Validity Check | Valid Value BUT with case/whitespaces mismatch '
                             f'| Erroneous Value: "{name}" | Possible match: "{possible_match}"')
        else:
            raise ValueError(f'Ontological Validity Check | Invalid Value | Erroneous Value: "{name}"')


"""-------Field Specific Checks [FC]-------"""


def check_for_nan_strings(cls, val):
    """
    Validator to check for 'nan' strings
    Args:
        cls:
        val:

    Returns:

    """
    if isinstance(val, str):
        if val.strip().lower() == 'nan':
            raise ValueError(f'Value Check | Invalid Value: "{val}" | Correct Value: "None"')
    return val


def check_dataset_id(cls, val):
    """
    Check that there should not be any spaces in dateset id value
    Args:
        val: value of the field

    Returns:
        val
    """
    if ' ' in val:
        raise ValueError(f'Value Check | Invalid value, contains one or more spaces. | Erroneous Value: "{val}"')
    return val


def check_valid_data_type(cls, val):
    """
    Check the value of data type against predefined values of data_type in valid_names.json
    Args:
        cls:
        val:

    Returns:

    """
    valid = VALID_NAMES["data_type"]
    if val not in valid:
        raise ValueError(f'Value Check | Invalid value, not one of the predefined values | Erroneous Value: "{val}"')
    return val


def check_year(cls, val):
    """
    Year has to be an integer and not greater than current year
    Args:
        val:

    Returns:
        val
    """
    is_int = True
    try:
        # converting to integer
        int(val)
    except ValueError:
        is_int = False
    if not is_int:
        if isinstance(val, str):
            if val != 'None':
                raise ValueError(f'Value Check | Invalid value | Erroneous Value: "{val}"')
    if is_int:
        if int(val) > dt.now().year or int(val) < 1900:
            raise ValueError(
                f'Value Check | Invalid value | Erroneous Value: "{val}"')
    return val


def check_valid_dataset_source(cls, val):
    """
    'dataset_source' can only be one of the predefined values.
    Args:
        val:

    Returns:
        val
    """
    valid = VALID_NAMES['dataset_source']
    if val not in valid:
        raise ValueError(f'Value Check | Invalid value, not one of the predefined values | Erroneous Value: "{val}"')
    return val


"""-------Ontology Value Checks [OC]-------"""


def check_for_default_values(cls, val, field):
    """
    Check for a single None value
    Args:
        val:
        field:

    Returns:

    """
    if len(val) < 2:
        return val
    field_to_check = field.name
    # field.name at times comes with a leading underscore
    field_to_check = field_to_check.strip('_')
    if field_to_check == 'curated_disease':
        if 'Normal' in val or "None" in val:
            raise ValueError(f'Value Check | Contains one or more default value "Normal" | Erroneous Value: "{val}"')
    else:
        if 'None' in val:
            raise ValueError(f'Value Check | Contains one or more default values. | Erroneous Value: "{val}"')
    return val


def has_valid_ontology(cls, val, field):
    """
    Check that the values of the above field case-sensitively match the valid values as in the ontology knowledge
    base
    Args:
        val:
        field:

    Returns:
        val
    """
    field_to_check = field.name
    # field.name at times comes with a leading underscore
    field_to_check = field_to_check.strip('_')
    if isinstance(val, list):
        for name in val:
            check_ontology(field_to_check, name)
    else:
        check_ontology(field_to_check, val)
    return val


"""-------Logical Checks [LC]--------"""


def check_cell_line_organism_agreement(cls, val, values, field):
    """
    Check that the value of cell line is valid for the particular organism
    Args:
        val: value of the field
        values: dict of values of the model object
        field: field being validated

    Returns:

    """
    field_to_check = field.name
    # field.name at times comes with a leading underscore
    field_to_check = field_to_check.strip('_')
    for value in val:
        if value != 'None' and value != 'none':
            if 'curated_organism' in values:
                organism_list = values.get('curated_organism')
                organisms_to_check_for_cell_line = {org: cell_lines for org, cell_lines in
                                                    VALID_NAMES[FIELD_MAPPING[field_to_check]]['organism'].items()
                                                    if org in organism_list}
                if organisms_to_check_for_cell_line:
                    if not any([True for v in organisms_to_check_for_cell_line.values() if value in v]):
                        raise ValueError(
                            f'Logical Check | Not a valid cell line for '
                            f'organism = {list(organisms_to_check_for_cell_line.keys())} | Erroneous Value: "{value}"')
    return val


def check_cell_line_disease_agreement(cls, val, values, field):
    """
    Check that the value of cell line is valid for the particular disease
    Args:
        val: value of the field
        values: dict of values of the model object
        field: field being validated

    Returns:

           """
    field_to_check = field.name
    # field.name at times comes with a leading underscore
    field_to_check = field_to_check.strip('_')
    for value in val:
        if value != 'None' and value != 'none':
            if 'curated_disease' in values:
                disease_list_from_input = values.get('curated_disease')
                diseases_to_check_for_cell_line = {disease: cell_lines for disease, cell_lines in
                                                   VALID_NAMES[FIELD_MAPPING[field_to_check]]['disease'].items()
                                                   if disease in disease_list_from_input}
                if diseases_to_check_for_cell_line:
                    if not any([True for v in diseases_to_check_for_cell_line.values() if value in v]):
                        raise ValueError(
                            f'Logical Check | Not a valid cell line for '
                            f'disease = {list(diseases_to_check_for_cell_line.keys())} | Erroneous Value: "{value}"')
    return val


"""---Function to dynamically build the schema_constructors given a repo---"""


def build_schema_for_repo(schema_dict):
    """
    given a repo, build two schema_constructors, one with just the schema, the other with validators as well
    Args:
        schema_dict:

    Returns:

    """
    # Build schema_constructors
    try:
        schema = build_validation_schema(schema_dict, for_level='dataset')
        all_fields = list(schema_dict.keys())
        ontological_fields_as_str, ontological_fields_as_list = split_curated_ontological_fields_by_type(
            ontological_fields,
            schema_dict)
        str_fields, list_fields = split_fields_by_type(schema_dict)
        validators = {
            'check_nan_strings': validator(*all_fields,
                                           allow_reuse=True,
                                           check_fields=False,
                                           each_item=True)(check_for_nan_strings),
            'check_dataset_id': validator('dataset_id',
                                          allow_reuse=True,
                                          check_fields=False)(check_dataset_id),
            'check_year': validator('year',
                                    allow_reuse=True,
                                    check_fields=False)(check_year),
            'check_valid_dataset_source': validator('dataset_source',
                                                    allow_reuse=True,
                                                    check_fields=False)(check_valid_dataset_source),
            'check_valid_data_type': validator('data_type',
                                               allow_reuse=True,
                                               check_fields=False)(check_valid_data_type),
            'check_cell_line_organism_agreement': validator('curated_cell_line',
                                                            allow_reuse=True,
                                                            check_fields=False)(check_cell_line_organism_agreement),
            'check_cell_line_disease_agreement': validator('curated_cell_line',
                                                           allow_reuse=True,
                                                           check_fields=False)(check_cell_line_disease_agreement)
        }

        if list_fields:
            validators['check_for_default_values'] = validator(*list_fields,
                                                               allow_reuse=True,
                                                               check_fields=False)(check_for_default_values)
        if ontological_fields_as_list:
            validators['check_valid_names_in_lists'] = validator(*ontological_fields_as_list,
                                                                 allow_reuse=True,
                                                                 each_item=True,
                                                                 check_fields=False)(has_valid_ontology)
        if ontological_fields_as_str:
            validators['check_valid_names_in_strings'] = validator(*ontological_fields_as_str,
                                                                   allow_reuse=True,
                                                                   check_fields=False)(has_valid_ontology)
        schema_with_validator = build_validation_schema(schema_dict, for_level='dataset', validators=validators)
        return schema, schema_with_validator
    except Exception as exc:
        print(tb.format_exc())
        print_exception()
        return None, None
