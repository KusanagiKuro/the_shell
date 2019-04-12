#!/usr/bin/env python3
from utility import insert_token_to_list
from escape_character import get_escaped_character
from param_expansion import process_dollar_sign


def get_double_quote_token(input_string, index, token_list):
    """
    Get the token created by the quoted string marked by the double quote

    Input:
        - input_string: The user's input
        - index: The index that marked the start of the quoted string
        - token_list: The list that the token will be added into

    Output:
        - index: The end index of the quoted string
    """
    # Initialize the token string
    token_string = ""
    # Initialize the token list for the double quote token
    content_list = []
    # Loop until an unquoted/unescaped double quote is found
    while True:
        # Loop until end of string is reached
        while index < len(input_string):
            # Increase index by one
            index += 1
            # Break if index is equal to the string's length
            if index == len(input_string):
                index -= 1
                break
            # Get current character at index position
            current_char = input_string[index]
            # If current character is a backslash, get escaped chracter
            if current_char == "\\":
                input_string, index, token_string = get_escaped_character(
                    input_string, index, token_string
                )
            # If current chracter is an unquoted/unescaped double quote,
            # add a double quote token to the token list, return the current
            # index
            elif current_char == "\"":
                insert_token_to_list(content_list, token_list,
                                     token_type="Double_Quote")
                return index
            # If current character is an unquoted/unescaped dollar sign,
            # get dollar sign expand (variable or parameter expansion)
            elif current_char == "$":
                index, token_string = process_dollar_sign(
                    input_string, index, content_list
                )
            # If current character is a <space>, insert the token string to
            # content list and reset it.
            elif current_char == " ":
                insert_token_to_list(token_string, content_list)
                token_string = ""
            # Else, just add current character to token string
            else:
                token_string += current_char
        # Ask user for more input if the quoted string is not closed
        input_string += "\n" + input(">")
    return index


def get_single_quote_token(input_string, index, token_list):
    """
    Get the token created by the quoted string marked by the single quote

    Input:
        - input_string: The user's input
        - index: The index that marked the start of the quoted string
        - token_list: The list that the token will be added into

    Output:
        - index: The end index of the quoted string
    """
    # Initialize the token string
    token_string = ""
    # Loop until another single quote is found
    while True:
        # Loop until end of string is reached
        while index < len(input_string):
            # Increase index by 1
            index += 1
            # Break if index is equal to the length of input string
            if index == len(input_string):
                break
            # Get current character
            current_char = input_string[index]
            # If current character is a single quote,
            # insert a single quote token to token list
            # with token string as its content
            if current_char is "'":
                insert_token_to_list(token_string, token_list,
                                     token_type="Single_Quote")
                return index
            # Else, add current character to token string
            else:
                token_string += current_char
        # Ask user for more input if the quoted string is not closed
        input_string += "\n" + input(">")
    return index
