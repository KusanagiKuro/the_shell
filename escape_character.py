#!/usr/bin/env python3


def get_escaped_character(input_string, index, token_string):
    try:
        next_char = input_string[index + 1]
    except IndexError:
        input_string += input(">")
        try:
            next_char = input_string[index + 1]
        except IndexError:
            next_char = ""
    token_string += next_char
    index += 1
    return input_string, index, token_string
