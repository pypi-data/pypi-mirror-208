"""
Validation utils
"""
from flask import request

from .prepare_json_response import prepare_json_response


def validate_generic_form(validation_class):
    """
    Generic validation form
    :param validation_class: Validation class
    :return: jsonfy | None
    """
    errors = validation_class().validate(request.json)
    if errors:
        return prepare_json_response('Validation Error', False, {'errors': errors}, 422)
    return None
