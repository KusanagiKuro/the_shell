#!/usr/bin/env python3
from readline import get_current_history_length, get_history_item


def read_file(file_name):
    contents = []
    with open(file_name, "r") as text_file:
        contents = text_file.readlines()
    return contents


def get_error_message(argument, error, command_name=None):
    return ""
# def write_file(file_name, mode="w+"):
#     with open(file_name, mode) as write


def get_history_log():
    history_log = []
    for index in range(1, get_current_history_length() + 1):
        history_log.append(get_history_item(index))
    return history_log