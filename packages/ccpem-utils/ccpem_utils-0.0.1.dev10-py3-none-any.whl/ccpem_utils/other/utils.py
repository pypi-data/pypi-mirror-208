import re


def extract_numeric_from_string(string):
    return re.findall(r"[-+]?(?:\d*\.*\d+)", string)
