#!/usr/bin/env python3


def read_file(file_name):
    contents = []
    with open(file_name, "r") as text_file:
        contents = text_file.readlines()
    return contents


def write_file(file_name, mode="w+"):
    with open(file_name, mode) as write


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
