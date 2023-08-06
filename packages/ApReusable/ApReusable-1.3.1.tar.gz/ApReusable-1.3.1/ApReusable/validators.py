import re


def validateEmail(email):
    match_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return match_pattern.match(email), email


def validateMobile(mobile):
    mobile_number = str(mobile).strip()
    if mobile_number[0] == "+":
        mobile_number = mobile_number[1:]
    match_pattern = re.compile(r'^\+?[1-9]\d{1,14}$')
    return match_pattern.match(mobile_number), mobile_number
