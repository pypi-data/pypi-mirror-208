import copy
import traceback as tb

import rapidfuzz as rf
from pydantic import validator

from polly_validator.settings import FIELD_MAPPING, VALID_NAMES
from polly_validator.utility.helper import build_validation_schema, list_to_set_in_dict, lower_and_strip, \
    print_exception, split_curated_fields_by_type, split_curated_ontological_fields_by_type

# Creating valid name but lowered and stripped
VALID_NAMES_LOWERED = copy.deepcopy(VALID_NAMES)
VALID_NAMES_LOWERED = lower_and_strip(VALID_NAMES_LOWERED)

# Convert all lists to set for faster lookups
VALID_NAMES = list_to_set_in_dict(VALID_NAMES)
VALID_NAMES_LOWERED = list_to_set_in_dict(VALID_NAMES_LOWERED)

ontological_fields = ['curated_disease',
                      'curated_cell_type',
                      'curated_cell_line',
                      'curated_drug',
                      'curated_tissue']
default_values = ['none', 'Normal']

"""Check for Nan values"""


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
            raise ValueError(f'Value Check | Invalid Value: "{val}" | Correct Value: "none"')
    return val


"""Ontology Check Function"""


def check_ontology(field_to_check, name):
    """

    Args:
        field_to_check:
        name:

    Returns:

    """
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


"""---Validator Functions---"""


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
        if 'Normal' in val or "none" in val:
            raise ValueError(
                f'Value Check | Contains one or more default value "Normal"/"none" | Erroneous Value: "{val}"')
    else:
        if 'one' in val:
            raise ValueError(f'Value Check | Contains one or more default values. | Erroneous Value: "{val}"')
    return val


def has_valid_ontology(cls, val, field):
    """
        Check that the values of the above field  match the valid values as in the ontology knowledge
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
    check_ontology(field_to_check, val)
    return val


"""---Function to dynamically build the schema_constructors given a repo---"""


def build_schema_for_repo(schema_dict):
    """
    given a repo, build two schema_constructors, one with just the schema, the other with validators as well
    Args:
        schema_dict:

    Returns:

    """
    try:
        schema = build_validation_schema(schema_dict, for_level='sample')
        all_curated_columns = [col_name for col_name in schema_dict if col_name.startswith('curated')]
        ontological_fields_as_str, ontological_fields_as_list = split_curated_ontological_fields_by_type(
            ontological_fields,
            schema_dict)
        str_fields, list_fields = split_curated_fields_by_type(all_curated_columns,
                                                               schema_dict)
        validators = {'check_for_nan_strings': validator(*all_curated_columns,
                                                         allow_reuse=True,
                                                         check_fields=False,
                                                         each_item=True)(check_for_nan_strings)}
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
        schema_with_validator = build_validation_schema(schema_dict, for_level='sample', validators=validators)
        return schema, schema_with_validator
    except Exception as exc:
        print(tb.format_exc())
        print_exception()
        return None, None
