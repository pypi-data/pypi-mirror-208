import re


def to_camel_case(x):
    """转驼峰法命名"""
    return re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)


def to_upper_camel_case(x):
    """转大驼峰法命名"""
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
    return s[0].upper() + s[1:]


def to_lower_camel_case(x):
    """转小驼峰法命名"""
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
    return s[0].lower() + s[1:]


def retain_filed_quotation(key, origin):
    if isinstance(origin, str) and key != "foreign_keys":
        origin = """%r""" % origin
    elif key in ["type", "type_"]:
        origin = """%r""" % origin
    return origin


def field_type_handle(field_type):
    return field_type


def dict2params_str(source: dict, ignore=True):
    foreign_key_str = ""
    if "foreign_keys" in source:
        foreign_keys = source.pop("foreign_keys")
        if foreign_keys:
            for foreign_key in foreign_keys:
                foreign_key_str += f'{foreign_key}, '
    others = []
    for k, v in source.items():
        if ignore:
            if v is False or v:
                others.append(f"{k}={retain_filed_quotation(k, v)}")
        else:
            others.append(f"{k}={retain_filed_quotation(k, v)}")
    other_str = ', '.join(others)
    return foreign_key_str + other_str
