#!/usr/bin/env python3
from token_definition import *


class Token_Pattern:
    operators = ['||', '|', '>', '<', '<<', '>>', '&&']

#################################
#            Utility            #
#################################


def get_escaped_character(input_string, index, token_string,
                          substitute_time=1):
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


def insert_token_to_list(content,
                         token_list,
                         position=None,
                         token_type="Word"):
    """
    Convert the content into a token and insert it to the list at
    certain position

    Input:
        - content: the content that will be converted
        - token_list: the list of tokens that the new token will be added
        to

    Output:
        - True if the token is added into the token list
        - False if no token is added into the token list
    """
    # Check if the input types are correct
    if ((isinstance(content, str) or isinstance(content, list)) and
            isinstance(token_list, list) and
            (isinstance(position, int) or
             position is None) and
            isinstance(token_type, str)) and content:
        # Create new token based on the token type
        if token_type == "Word":
            new_token = Word_Token(content)
        elif token_type == "Operator":
            new_token = Operator_Token(content)
        elif token_type == "Single_Quote":
            new_token = Single_Quote_Token(content)
        elif token_type == "Double_Quote":
            new_token = Double_Quote_Token(content)
        elif token_type == "Param_Expand":
            new_token = Param_Expand_Token(content)
        elif token_type == "Subshell":
            new_token = Subshell_Token(content)
        elif token_type == "Command_Substitution":
            new_token = Command_Substitute_Token(content)
        elif token_type == "Variable":
            new_token = Variable_Token(content)
        elif token_type == "Param_Value":
            new_token = Param_Value_Token(content)
        # If the token type matches none of the above, there
        # will be no token added into the list
        else:
            return False
        # If there is no position being specified, add the new
        # token to the end of the list
        if position is None:
            token_list.append(new_token)
        # Else insert it to the list at the position
        else:
            token_list.insert(position, new_token)
        return True
    return False

#################################
#            Quoting            #
#################################


def get_double_quote_token(input_string, index, token_list,
                           substitute_time=1):
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
                    input_string, index, token_string, substitute_time
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
                    input_string, index, token_string, content_list
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

#################################
#     Dollar Sign Processing    #
#################################


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


def process_dollar_sign(input_string, index, token_string, token_list):
    end_index = get_dollar_sign_expand(input_string, index,
                                       token_list)
    # If the end index of dollar sign expand is the same as the
    # current index (meaning the dollar sign stand alone), append
    # it to the token string
    if end_index == index:
        token_string += current_char
    # Else, insert the previous token string to the content list,
    # reset the token string and set index equal to the end index
    else:
        insert_token_to_list(token_string, token_list, -1)
        token_string = ""
        index = end_index
    return index, token_string


#################################
#           Main Lexer          #
#################################


def get_token_list(input_string, index=0, subshell=False,
                   command_substitute=False):
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
                input_string, index, token_string, token_list
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
