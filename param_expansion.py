#!/usr/bin/env python3
from utility import insert_token_to_list
from quoting import get_double_quote_token, get_single_quote_token
from escape_character import get_escaped_character


def get_param_expansion(input_string, index, token_list):
    token_string = ""
    content_list = []
    param_name = ""
    param_operator = ""
    param_value = ""
    index += 2
    while True:
        if not param_operator and not param_value:
            index, param_name = get_param_name(
                input_string, index, content_list, param_name
            )
        if not param_value:
            index, param_operator = get_param_operator(
                input_string, index, content_list, param_operator
            )
        index, param_value = get_param_value(
            input_string, index, content_list, param_value
        )
        try:
            current_char = input_string[index]
            if current_char == "}":
                insert_token_to_list(content_list if content_list
                                     else [None],
                                     token_list,
                                     token_type="Param_Expand")
                return index
        except IndexError:
            pass
        input_string += "\n" + input(">")
    return index


def get_param_name(input_string, index, token_list, current_value):
    """
    Get the parameter name in the parameter expansion

    Input:
        - input_string: The user's input
        - index: The index that marked the start of the parameter name
        - token_list: The list that the token will be added into

    Output:
        - index: The end index of the parameter name
    """
    token_string = current_value
    content_list = []
    while index < len(input_string):
        current_char = input_string[index]
        if current_char.isalnum() or current_char is "_":
            token_string += current_char
        elif current_char is "}":
            insert_token_to_list(token_string, token_list,
                                 token_type="Variable")
            return index, token_string
        else:
            insert_token_to_list(token_string, token_list,
                                 token_type="Variable")
            break
        index += 1
    return index, token_string


def get_param_operator(input_string, index, token_list, current_value):
    operators = ["##", "%%", "%", "#", ":", ":?", ":-",
                 ":=", ":+"]
    previous_char = ""
    token_string = current_value
    while index < len(input_string):
        current_char = input_string[index]
        if token_string + current_char not in operators:
            insert_token_to_list(token_string, token_list,
                                 token_type="Operator")
            return index, token_string
        elif current_char is "}":
            return index, token_string
        else:
            token_string += current_char
        index += 1
    return index, token_string


def get_param_value(input_string, index, token_list, current_value):
    previous_char = ""
    token_string = current_value
    content_list = []
    while index < len(input_string):
        current_char = input_string[index]
        if current_char == " " and not token_string:
            pass
        elif current_char == "\\":
            input_string, index, token_string = get_escaped_character(
                input_string, index, token_string
            )
        elif current_char == "}":
            insert_token_to_list(token_string, content_list,
                                 token_type="Word")
            insert_token_to_list(content_list, token_list,
                                 token_type="Param_Value")
            return index, token_string
        elif current_char == ":":
            insert_token_to_list(token_string, content_list,
                                 token_type="Word")
            insert_token_to_list(":", content_list,
                                 token_type="Operator")
            token_string = ""
        elif current_char == " " or current_char == "\n":
            insert_token_to_list(token_string, content_list,
                                 token_type="Word")
            token_string = ""
        else:
            token_string += current_char
        index += 1
    insert_token_to_list(token_string, content_list,
                         token_type="Word")
    return index, token_string


def get_variable(input_string, index, token_list):
    previous_char = input_string[index]
    token_string = ""
    while index < len(input_string):
        try:
            current_char = input_string[index + 1]
            if current_char.isalnum() or current_char is "_":
                token_string += current_char
            elif token_string:
                insert_token_to_list(token_string, token_list,
                                     token_type="Variable")
                return index
            else:
                return index
        except IndexError:
            if token_string:
                insert_token_to_list(token_string, token_list,
                                     token_type="Variable")
            break
        index += 1
    return index


def get_dollar_sign_expand(input_string, index, token_list):
    """
    Get the token marked by the dollar sign
    """
    try:
        next_character = input_string[index + 1]
        # If the next character is a curly bracket, this means it's
        # a parameter expansion. Return the end index of that parameter
        # expansion
        if next_character == "{":
            return get_param_expansion(input_string, index,
                                       token_list)
        # If next character is a letter or an underscored, it's a
        # variable. Return the end index of that variable token
        elif next_character.isalpha() or next_character is "_":
            return get_variable(input_string, index, token_list)
        # Else the dollar sign doesn't have special meaning
        else:
            return index
    except IndexError:
        return index


def process_dollar_sign(input_string, index, content_list):
    end_index = get_dollar_sign_expand(input_string, index,
                                       content_list)
    # If the end index of dollar sign expand is the same as the
    # current index (meaning the dollar sign stand alone), append
    # it to the token string
    if end_index == index:
        token_string += current_char
    # Else, insert the previous token string to the content list,
    # reset the token string and set index equal to the end index
    else:
        insert_token_to_list(token_string, content_list, -1)
        token_string = ""
        index = end_index
    return index, token_string
