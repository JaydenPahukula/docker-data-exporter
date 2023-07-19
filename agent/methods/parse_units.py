import re

byte_units = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30, "TB": 2**40}

def parseByteUnits (input: str) -> int:
    """
    This helper function takes in a string and converts it into bytes.
    For example: parseByteUnits("10.43KB") == 10680
    """

    # getting
    input = input.upper()
    if not re.match(r' ', input):
        input = re.sub(r'([KMGT]?B)', r' \1', input)
    number, unit = [string.strip() for string in input.split()]
    
    return int(float(number) * byte_units[unit])