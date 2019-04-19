#!/usr/bin/env python3
from fnmatch import fnmatch


def use_default_values(parameter, operator, value, variables_dict):
    if operator == ':-':
        return variables_dict[parameter] if\
               parameter in variables_dict and variables_dict[parameter] != ''\
               else value
    elif operator == '-':
        return variables_dict[parameter] if\
               parameter in variables_dict\
               else value


def assign_default_values(parameter, operator, value, variables_dict):
    if operator == ':=':
        if parameter in variables_dict and variables_dict[parameter] != '':
            return variables_dict[parameter]
    elif operator == '=':
        if parameter in variables_dict:
            return variables_dict[parameter]
    variables_dict[parameter] = value
    return value


def use_alternative_value(parameter, operator, value, variables_dict):
    if operator == ':+':
        return value if parameter in variables_dict and\
               variables_dict[parameter] != '' else ''
    elif operator == '+':
        return value if parameter in variables_dict else ''


def find_match_char(a_list, pattern):
    list_match_idx = []
    for idx, char in enumerate(a_list):
        if fnmatch(a_list[:idx + 1], pattern):
            list_match_idx.append(idx)
    return list_match_idx


def remove_suffix(param_value, operator, value):
    param_value = param_value[::-1]
    value = value[::-1]
    if find_match_char(param_value, value):
        if operator == '%':
            return param_value[find_match_char(param_value,
                                               value)[0] + 1:][::-1]
        elif operator == '%%':
            return param_value[find_match_char(param_value,
                                               value)[-1] + 1:][::-1]
    else:
        return param_value[::-1]


def remove_prefix(param_value, operator, value):
    if find_match_char(param_value, value):
        if operator == '#':
            return param_value[find_match_char(param_value,
                                               value)[0] + 1:]
        elif operator == '##':
            return param_value[find_match_char(param_value,
                                               value)[-1] + 1:]
    else:
        return param_value


def exe_remove(parameter, operator, value, variables_dict):
    if parameter in variables_dict:
        param_value = variables_dict[parameter]
        if '#' in operator:
            return remove_prefix(param_value, operator, value)
        elif '%' in operator:
            return remove_suffix(param_value, operator, value)
    else:
        return ''


def expand_parameter(parameter, operator, value, variables_dict):
    if '-' in operator:
        return use_default_values(parameter, operator,
                                  value, variables_dict)
    elif '+' in operator:
        return use_alternative_value(parameter, operator,
                                     value, variables_dict)
    elif '=' in operator:
        return assign_default_values(parameter, operator,
                                     value, variables_dict)
    elif '?' in operator:
        return indicate_error(parameter, operator,
                              value, variables_dict)
    elif '#' in operator or '%' in operator:
        return exe_remove(parameter, operator,
                          value, variables_dict)


def indicate_error(parameter, operator, value, variables_dict):
    if operator == ':?':
        if parameter in variables_dict and variables_dict[parameter] != '':
            return variables_dict[parameter]
        else:
            print('intek-sh: ' + parameter + ': parameter null or not set')
            exit = True


# A = {'abc': '$$$src/cmd', 'xyz': ''}
# names = 'xyz'
# print(expand_parameter(names, ':=', 'word', A))
