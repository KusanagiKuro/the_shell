#!/usr/bin/env python3
from token_definition import *
from exception import *


def expand_and_substitute(token_list, shell_variable_dict, shell_environ_dict):
    result_string = ""
    for token in token_list:
        result_string += expand_and_substitute_token(token,
                                                     shell_variable_dict,
                                                     shell_environ_dict)


def expand_and_substitute_token(token,
                                shell_variable_dict,
                                shell_environ_dict,
                                globbing=True):
    token_processing_functions = {
        Word_Token: expand_and_substitute_word,
        Operator_Token: expand_and_substitute_operator,
        Subshell_Token: expand_and_substitute_subshell,
        Param_Expand_Token: expand_and_substitute_param_expand,
        Double_Quote_Token: expand_and_substitute_double_quote,
        Single_Quote_Token: expand_and_substitute_single_quote,
        Variable_Token: expand_and_substitute_variable,
        Seperator_Token: expand_and_substitute_separator
    }
    try:
        return token_processing_functions[type(token)](
            token, shell_variable_dict, shell_environ_dict
        )
    except KeyError:
        return ""


def expand_and_substitute_word(token,
                               shell_variable_dict,
                               shell_environ_dict,
                               globbing=True):
    if not globbing:
        return token.content
    else:
        return " ".join(process_globbing(token.content))


def expand_and_substitute_operator(token,
                                   shell_variable_dict,
                                   shell_environ_dict,
                                   globbing=True):
    return token.content


def expand_and_substitute_subshell(token,
                                   shell_variable_dict,
                                   shell_environ_dict,
                                   globbing=True):
    pass


def expand_and_substitute_param_expand(token,
                                       shell_variable_dict,
                                       shell_environ_dict,
                                       globbing=True):
    pass


def expand_and_substitute_double_quote(token,
                                       shell_variable_dict,
                                       shell_environ_dict,
                                       globbing=True):
    final_string = ""
    for child_token in token.content:
        final_string += expand_and_substitute_token(child_token,
                                                    shell_variable_dict,
                                                    shell_environ_dict,
                                                    False)
    return final_string


def expand_and_substitute_single_quote(token,
                                       shell_variable_dict,
                                       shell_environ_dict,
                                       globbing=True):
    return token.content


def expand_and_substitute_separator(token,
                                    shell_variable_dict,
                                    shell_environ_dict,
                                    globbing=True):
    return token.content


def expand_and_substitute_variable(token,
                                   shell_variable_dict,
                                   shell_environ_dict):
    combined_dict = {**shell_environ_dict, **shell_environ_dict}
    return combined_dict.get(token.content, None)
