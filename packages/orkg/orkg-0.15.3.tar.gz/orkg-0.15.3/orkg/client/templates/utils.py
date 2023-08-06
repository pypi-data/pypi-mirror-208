import datetime
import keyword
import re
from typing import Union, List

Number = Union[int, float, complex, List[int], List[float], List[complex]]
Boolean = Union[bool, List[bool]]
String = Union[str, List[str]]
Integer = Union[int, List[int]]
Date = Union[datetime.date, List[datetime.date]]


def clean_up_dict(dictionary: dict) -> dict:
    """
    replaces the key 'name' with 'label' inside the 'resource' object.
    then strips the root key 'resource' and returns the inner dictionary.
    """
    dictionary = dictionary['resource']
    dictionary['label'] = dictionary['name']
    del dictionary['name']
    return dictionary


def pre_process_string(string: str) -> str:
    lower_string = string.lower().replace(' ', '_')
    res = re.sub(r'\W+', '', lower_string)
    return res


def check_against_keywords(string: str) -> str:
    """
    Checks a string against python keywords.
    If a keyword is found, it is postfixed with a '_template'.
    """
    if string in keyword.kwlist:
        return string + '_template'
    return string


def map_type_to_pythonic_type(value_type: str) -> str:
    if value_type == 'Number':
        return 'Number'
    elif value_type == 'Boolean':
        return 'Boolean'
    elif value_type == 'Integer':
        return 'Integer'
    elif value_type == 'Date':
        return 'Date'
    else:
        return 'String'


def remove_empty_values(dictionary: dict):
    if 'values' not in dictionary['resource']:
        return
    for _, value in dictionary['resource']['values'].items():
        for v in value:
            if not bool(v):
                value.remove(v)
