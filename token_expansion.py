#!/usr/bin/env python3
from token_definition import Double_Quote_Token, Single_Quote_Token,\
                             Param_Expand_Token, Param_Value_Token,\
                             Variable_Token, Operator_Token, Word_Token,\
                             Subshell_Token, Separator_Token, Token
from exception import UnexpectedTokenError, BadSubstitutionError
from param_expansion import expand_parameter
from globbing import globbing
from shell import Shell


def find_next_element_of_type_in_list(search_list, matching_type):
    """
    Find the next element that has the matching type from a list

    Input:
        - search_list: a list who needs to be in 
    """
    for item in search_list:
        if isinstance(item, matching_type):
            return item
    return None


def expand_word_token(token, shell, apply_globbing):
    if apply_globbing:
        return [str(item) for item in globbing(token.content)]
    else:
        return token.content


def expand_double_quote(token, shell):
    """
    Return the final string after all expansions happened inside the double
    quote

    Input:
        - token: a Double_Quote_Token object that needs to be expanded
        - shell: a Shell object whose local variables are used in the expansion

    Output:
        - content_string: final string after expansion
    """
    # Validate input
    if not isinstance(token, Double_Quote_Token):
        print("token parameter must be a Double_Quote_Token object")
        return ""
    elif not isinstance(shell, Shell):
        print("shell parameter must be a Shell object")
        return ""
    # If there is nothing inside the double quote, return an empty string
    if None in token.content:
        return ""
    # Initialize the variable that will hold the return string
    return_string = ""
    # Loop through the token list of the double quote token
    for child_token in token.content:
        # If the child token is an operator/word/separator token
        if isinstance(child_token, (Operator_Token,
                                    Word_Token,
                                    Separator_Token)):
            # Add its content string into the return string
            return_string += child_token.content
        # Elif the token is a parameter expansion
        elif isinstance(child_token, Param_Expand_Token):
            # Expand it and add the result into the return string
            return_string += expand_parameter_token(child_token, shell, False)
        # Elif the child token is a variable token
        elif isinstance(child_token, Variable_Token):
            # Expand it and add the result into the return string
            return_string += expand_variable(child_token, shell)
        else:
            raise UnexpectedTokenError(token.original_string)
    # Return result string
    return return_string


def expand_variable(token, shell):
    """
    Return the value of variable from the shell local variable dictionary
    as a string

    Input:
        - token: a Variable_Token object that needs to be expanded
        - shell: a Shell object whose local variables are used in the expansion

    Output:
        - The string of the value of the Variable_Token retreived from
        the shell's local variable dictionary
    """
    # Validate input
    if not isinstance(token, Variable_Token):
        print("token parameter must be a Variable_Token object")
        return ""
    elif not isinstance(shell, Shell):
        print("shell parameter must be a Shell object")
        return ""
    return str(shell.local_variable.get(token.content, ""))


def expand_parameter_token(token, shell, apply_globbing=True):
    """
    Return the final string after processing the parameter expansion

    Input:
        - token: a Param_Expand_Token object that needs to be expanded
        - shell: a Shell object whose local variables are used in the expansion

    Output:
        - The string after processing the parameter expansion
    """
    # Validate input
    if not isinstance(token, Param_Expand_Token):
        print("token parameter must be a Variable_Token object")
        return ""
    elif not isinstance(shell, Shell):
        print("shell parameter must be a Shell object")
        return ""
    # Find the variable token in the parameter token's list
    variable_token = find_next_element_of_type_in_list(
        token.content, Variable_Token
    )
    # Raise error if there is no variable token found.
    if not variable_token:
        raise BadSubstitutionError(token.original_string)
    # Find the operator token and get its string
    operator_token = find_next_element_of_type_in_list(token.content,
                                                       Operator_Token)
    operator_string = operator_token.content if operator_token else ""
    # Find the parameter value token
    value_token = find_next_element_of_type_in_list(token.content,
                                                    Param_Value_Token)
    # Expand the value token if needed
    value_string = expand_parameter_value_token(value_token, shell, apply_globbing)
    # Return the string after expansion
    string = expand_parameter(variable_token.content,
                              operator_string,
                              value_string,
                              shell.local_variable)
    return string


def expand_parameter_value_token(token, shell, apply_globbing):
    """
    Return the string after expanding the parameter value token

    Input:
        - token: a Param_Value_Token object that needs to be expanded
        - shell: a Shell object whose local variables are used in the expansion
        - apply_globbing: a boolean value that determines whether globbing will be
        applied on the token inside
    """
    # Validate input
    if not isinstance(token, Param_Value_Token):
        print("token parameter must be a Param_Value_Token object")
        return ""
    elif not isinstance(shell, Shell):
        print("shell parameter must be a Shell object")
        return ""
    # Return an empty string if the content list of the token is empty
    if None in token.content:
        return ""
    # Initialize the return string
    return_string = ""
    # Loop through the token in its token list
    for child_token in token.content:
        # Add the result of expanding the child token to the return string
        expand_child_object = expand_token(child_token, shell, apply_globbing)
        if isinstance(expand_child_object, str):
            return_string += expand_child_object
        elif isinstance(expand_child_object, list):
            return_string += " ".join([str(item) for item in expand_child_object])
    return return_string


def expand_token(token, shell, apply_globbing=True):
    """
    Get the string after apply expansion and globbing on all the tokens.

    Input:
        - token: a Token object that needs to be expanded
        - shell: a Shell object whose local variables are used in the expansion
        - apply_globbing: a boolean value that determines whether globbing will be
        applied on the token inside

    Output:
        - The string after expansion
    """
    # Validate input
    if not isinstance(token, Token):
        print("token parameter must be a Token object")
        return ""
    elif not isinstance(shell, Shell):
        print("shell parameter must be a Shell object")
        return ""
    # Check token type and process base on its type
    if isinstance(token, (Operator_Token, Separator_Token, Subshell_Token)):
        return token.content
    elif isinstance(token, Word_Token):
        return expand_word_token(token, shell, apply_globbing)
    elif isinstance(token, Param_Expand_Token):
        return expand_parameter_token(token, shell, apply_globbing)
    elif isinstance(token, Variable_Token):
        return expand_variable(token, shell)
    elif isinstance(token, Double_Quote_Token):
        return expand_double_quote(token, shell)
    elif isinstance(token, Single_Quote_Token):
        return token.content.strip("'")


def expand_token_list(token_list, shell):
    """
    Get the string after expanding a token list

    Input:
        - token_list: a token list that needs to be expanded
        - shell: a Shell object whose local variables are used in the expansion
    """
    expanded_list = []
    for token in token_list:
        expanded_object = expand_token(token, shell)
        if isinstance(expanded_object, str):
            expanded_list.append(expanded_object)
        elif isinstance(expanded_object, list):
            expanded_list.extend(expanded_object)
    return expanded_list


def expand_token_for_command_list(command_list, shell):
    """
    Get the argument list for the command list after processing
    shell expansion

    Input:
        - token: a command list whose commands needs to be expanded
        - shell: a Shell object whose local variables are used in the expansion
    """
    for command in command_list:
        command.argument_list = expand_token_list(command.token_list, shell)
        command.stdout = expand_token_list(command.stdout, shell)
        command.stdin = expand_token_list(command.stdin, shell)
