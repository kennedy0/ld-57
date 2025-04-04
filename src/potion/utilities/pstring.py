import re


def remove_special_characters(s: str) -> str:
    """ Remove all non-alphanumeric characters from a string. """
    return re.sub('[^a-zA-Z0-9]', '', s)
