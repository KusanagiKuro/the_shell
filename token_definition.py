#!/usr/bin/env python3
from exception import BadSubstitutionError


class Token_Pattern:
    operators = ['\|\|', '\|', '>', '<', '<<', '>>', '&&']


class Token:
    def __init__(self, content):
        self._content = content

    def parse(self, environ_variable_dict={}, shell_variable_dict={}):
        pass

    def __str__(self):
        pass

    def get_original_string(self):
        return self._content


class Word_Token(Token):
    def parse(self, environ_variable_dict,
              shell_variable_dict):
        return self._content

    def __str__(self):
        return "Word(%s)" % str(self._content)


class Double_Quote_Token(Token):
    def parse(self, environ_variable_dict,
              shell_variable_dict):
        return "".join([item.parse() for item in self._content])

    def __str__(self):
        return "Double_Quote(%s)" % ", ".join([str(item)
                                              for item in self._content])

    def get_original_string(self):
        return "\"%s\"" % "".join([item.get_original_string()
                                   for item in self._content])


class Single_Quote_Token(Token):
    def parse(self, environ_variable_dict, shell_variable_dict=None):
        return " ".join([item.parse() for item in self._content])

    def __str__(self):
        return "Single_Quote(%s)" % str(self._content)

    def get_original_string(self):
        return "'%s'" % self._content


class Param_Expand_Token(Token):
    def parse(self, environ_variable_dict={}, shell_variable_dict={}):
        pass

    def __str__(self):
        return "Param_Expand(%s)" % ", ".join([str(item)
                                              for item in self._content])

    def get_original_string(self):
        if self._content[0] is None:
            return "$\{\}"
        if len(self._content) == 1:
            return "${%s}" % self._content[0].get_original_string()
        elif len(self._content) == 2:
            return "${%s%s}" % (self.content[0].get_original_string(),
                                self.content[1].get_original_string())
        else:
            return "${%s%s%s}" % (self.content[0].get_original_string(),
                                  self.content[1].get_original_string(),
                                  self.content[2].get_original_string())


class Operator_Token(Token):
    def parse(self, environ_variable_dict={}, shell_variable_dict={}):
        return self._content

    def __str__(self):
        return "Operator(%s)" % str(self._content)


class Variable_Token(Token):
    def parse(self, environ_variable_dict={}, shell_variable_dict={}):
        return shell_variable_dict.get(self._content, "")

    def __str__(self):
        return "Variable(%s)" % str(self._content)

    def get_original_string(self):
        return "$%s" % self._content


class Param_Value_Token(Token):
    def parse(self, environ_variable_dict={}, shell_variable_dict={}):
        if (self._content[0] is None or
                not (isinstance(self._content[0], Variable_Token) or
                     isinstance(self._content[0], Operator_Token))):
            raise BadSubstitutionError(self.get_original_string())

    def __str__(self):
        return "Param_Value(%s)" % ", ".join([str(item)
                                             for item in self._content])

    def get_original_string(self):
        return "".join([item.get_original_string() for item in self._content])


class Subshell_Token(Token):
    def parse(self, environ_variable_dict={}, shell_variable_dict={}):
        pass

    def __str__(self):
        return "Subshell(%s)" % ", ".join([str(item)
                                           for item in self._content])

    def get_original_string(self):
        return "".join([item.get_original_string() for item in self._content])


class Seperator_Token(Token):
    def __str__(self):
        return "Seperator()"

    def get_original_string(self):
        return " "


class Command:
    def __init__(self, argument_list, stdin=None, stdout=None):
        self.command = argument_list[0]
        self.argument = argument_list[1:]
        self.stdin = stdin
        self.stdout = stdout

    def execute(self, subshell=True):
        pass


class Command_List:
    def __init__(self, *args):
        pass