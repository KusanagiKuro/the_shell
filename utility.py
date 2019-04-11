#!/usr/bin/env python3


def read_file(file_name):
    contents = []
    with open(file_name, "r") as text_file:
        contents = text_file.readlines()
    return contents


def write_file(file_name, mode="w+"):
    with open(file_name, mode) as write
