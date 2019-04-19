#!/usr/bin/env python3
from token_definition import *
from exception import *


def expand_double_quote(token, shell):
    content_string = ""
    if None in token.content:
        return content_string
    for child_token in token.content:
        if (isinstance(child_token, Operator_Token) or
                isinstance(child_token, Separator_Token) or
                isinstance(child_token, Word_Token)):
            content_string += child_token.content
        elif isinstance(child_token, Param_Expand_Token):
            content_string += expand_parameter_token(child_token, shell, False)
        elif isinstance(child_token, Variable_Token):
            content_string += expand_variable(child_token, shell, False)
    return content_string


def expand_variable(token, shell):
    return str(shell.local_variable_dict.get(token.content, ""))


def expand_parameter_token(token, shell, glob=True):
    content_string = ""
    if None in token.content:
        raise BadSubstitutionError(token.original_string)
    return content_string



def expand_token(token, shell):
    if isinstance(token, Operator_Token) or isinstance(token, Separator_Token):
        return token.content
    elif isinstance(token, Word_Token):
        return expand_word_token(token, shell)
    elif isinstance(token, Param_Expand_Token):
        return expand_parameter_token(token, shell, True)
    elif isinstance(token, Variable_Token):
        return expand_variable(token, shell, True)
    elif isinstance(token, Double_Quote_Token):
        return expand_double_quote(token, shell, False)
    elif isinstance(token, Single_Quote_Token):
        return token.content.strip("'")
