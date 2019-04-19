#!/usr/bin/env python3
from re import match
from glob import glob
from itertools import product


def find_spec_char(a_string):
    '''
    find special characters in a string
    @param: considered string
    return: True if any special character in the string
            False if no any special character in the string
    '''
    return False if match("^[a-zA-Z0-9_.,~/]*$", a_string) else True


def expand_dot(a_string):
    dot_expand_list = []
    for part in a_string.split('/'):
        if part == '.*':
            dot_expand_list.append(['.', '..', '.*'])
        elif part == '..*':
            dot_expand_list.append(['..', '..*'])
        else:
            dot_expand_list.append([part])
    return dot_expand_list


def globbing(a_string):
    if find_spec_char(a_string):
        dot_expand_list = list(product(*expand_dot(a_string)))
        path_expand_list = ['/'.join(item) for item in dot_expand_list]
        glob_expand_list = []
        for item in sorted(path_expand_list):
            glob_expand_list.extend(glob(item))
        return sorted(glob_expand_list) if glob_expand_list else [a_string]
    else:
        return [a_string]
