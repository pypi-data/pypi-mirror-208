import datetime

from mathtext.constants import TOKENS2INT_ERROR_INT


def is_type_exponent(expected_answer):
    """ Checks for a ^ in the expected_answer

    Currently only exponent answers have a ^
    """
    if "^" in expected_answer:
        return True
    return False


def is_type_fraction(expected_answer):
    """ Checks for a / in the expected_answer

    Currently only fraction answers have a /
    """
    if "/" in expected_answer:
        return True
    return False


text_type_answers = {
    'yes-no': ['yes', 'no'],
    'true-false': ['t', 'f'],
    'multiple-choice': ['a', 'b', 'c', 'd'],
    'even-odd': ['even', 'odd'],
    'day-of-the-week': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
}

symbol_type_answers = {
    '>': ['>', 'g', 'gt', 'greater'],
    '<': ['<', 'l', 'lt', 'less'],
    '>=': ['>=', 'gte'],
    '<=': ['<=', 'lte'],
    '=': ['=', 'e', 'equal'],
}


def is_type_text_or_symbol(expected_answer, answer_options):
    """ Searches the possible answers within text or symbol question types for a match """
    for answer_type in answer_options:
        if expected_answer.lower() in answer_options[answer_type]:
            return True
    return False


def is_type_time(expected_answer):
    """ Checks for a : in the expected_answer

    Currently only time answers have a:
    """
    if ":" in expected_answer:
        return True
    return False


def is_type_multiplication_equation(expected_answer):
    """ Checks for an x in the expected_answer

    Currently only multiplication equations answer types have an x
    """
    if "x" in expected_answer:
        return True
    return False


def check_answer_type(expected_answer):
    """ Determines if the expected answer is not a float or int

    >>> check_answer_type("2 ^ 5")
    "exponent"

    >>> check_answer_type("11: 30 PM")
    "time"

    >>> check_answer_type("T")
    "text"

    >>> check_answer_type("2")
    "other"
    """
    if is_type_exponent(expected_answer):
        return 'exponent'
    if is_type_fraction(expected_answer):
        return 'fraction'
    if is_type_time(expected_answer):
        return 'time'
    if is_type_text_or_symbol(expected_answer, text_type_answers):
        return 'text'
    if is_type_text_or_symbol(expected_answer, symbol_type_answers):
        return 'symbol'
    if is_type_multiplication_equation(expected_answer):
        return 'equation'

    return 'other'
