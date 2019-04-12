#!/usr/bin/env python3
from token_definition import *
from param_expansion import get_dollar_sign_expand
from quoting import get_double_quote_token, get_single_quote_token
from escape_character import get_escaped_character
from utility import insert_token_to_list


class Token_Pattern:
    operators = ['||', '|', '>', '<', '<<', '>>', '&&']


def get_token_list(input_string, index=0, subshell=False):
    """
    Convert the user input into a token list

    Input:
        - input_string: The string that the user has input

    Output:
        - token_list: the list of tokens after conversion
        - None if the input is incorrect
    """
    # If the input is incorrect, return None
    if not isinstance(input_string, str):
        print("input_string parameter must be a str type object")
        return None
    # Initialize the token list and token string (which will be used
    # to convert into token)
    token_list = []
    token_string = ''
    # Initialize a variable to track the index
    index = 0
    # Initialize a variable to track the previous character
    previous_char = ""
    # Loop through the input string one by one.
    while index < len(input_string):
        # Get current character at current index
        current_char = input_string[index]
        # Check to see if current character match any
        # criteria and process depends on that criteria
        # If previous character and current character can be combined
        # to create an operator
        if previous_char + current_char in Token_Pattern.operators:
            # Add current character to token string
            token_string = previous_char + current_char
        # Else if current character can be an operator
        elif current_char in Token_Pattern.operators:
            # Convert and add current token string to token list
            insert_token_to_list(token_string, token_list)
            # New token string starts with current character
            token_string = current_char
        # Else if the token string is an operator
        elif token_string in Token_Pattern.operators:
            # Convert and add current token string as an operator token
            # to token list
            insert_token_to_list(token_string, token_list,
                                 "Operator")
            # New token string starts with current character
            token_string = current_char
        # Else if current character is a <backslash>
        elif current_char == "\\":
            input_string, index, token_string = get_escaped_character(
                input_string, index, token_string
            )
        # Else if current character is a $
        elif current_char == "$":
            index, token_string = process_dollar_sign(
                input_string, index, token_list
            )
        # Else if current character is a <double_quote>
        # or a <space>
        # or a <single_quote>
        # or left parentheses
        elif (current_char == "\"" or current_char == "'" or
              current_char == "(" or current_char == " "):
            # Convert and add current token string to token list
            insert_token_to_list(token_string, token_list)
            # New token string will be empty
            token_string = ""
            # If current character is not a <space>
            if current_char != " ":
                # Initialize the dictionary that contains the name of
                # the functions that will get the token
                get_token_functions = {
                    "\"": get_double_quote_token,
                    "'": get_single_quote_token
                    # "(": get_subshell_token
                }
                # Run the get token function base on the current character
                # and return the index
                index = get_token_functions[current_char](
                    input_string, index, token_list
                )
        # Else add current character to token string
        else:
            token_string += current_char
        # Increase index by 1
        index += 1
        # Set previous character to current character
        previous_char = current_char
    # Add the current token string into the token list
    insert_token_to_list(token_string, token_list)
    return token_list
