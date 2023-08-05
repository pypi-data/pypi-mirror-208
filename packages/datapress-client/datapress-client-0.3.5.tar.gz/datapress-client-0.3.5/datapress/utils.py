import re


def check_key_for_errors(key):
    """
    Will DataPress recognise this as a valid
    lowercase-with-dashes key?
    """
    if type(key) != str:
        return 'Must be a string'
    if len(key) > 64:
        return 'Maximum 64 characters'
    if len(key) < 3:
        return 'Minimum 3 characters'
    if not re.match(r'^[a-zA-Z0-9-_]+$', key):
        return 'Must be composed of letters, numbers, dashes and underscores'
    if not re.match(r'.*[a-zA-Z].*', key):
        return 'Must contain at least one letter'
    if not re.match(r'^[a-z0-9]', key):
        return 'Must start with a lowercase letter or number'
    #  No errors
    return None
