# Generated from /home/popovms/course/dockerfile-ansible-convert/src/ansible_matcher/example_based/antlr/grammar/CommandTemplateParser.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CommandTemplateParser import CommandTemplateParser
else:
    from CommandTemplateParser import CommandTemplateParser

# This class defines a complete listener for a parse tree produced by CommandTemplateParser.
class CommandTemplateParserListener(ParseTreeListener):

    # Enter a parse tree produced by CommandTemplateParser#command_template.
    def enterCommand_template(self, ctx:CommandTemplateParser.Command_templateContext):
        pass

    # Exit a parse tree produced by CommandTemplateParser#command_template.
    def exitCommand_template(self, ctx:CommandTemplateParser.Command_templateContext):
        pass


    # Enter a parse tree produced by CommandTemplateParser#template_part.
    def enterTemplate_part(self, ctx:CommandTemplateParser.Template_partContext):
        pass

    # Exit a parse tree produced by CommandTemplateParser#template_part.
    def exitTemplate_part(self, ctx:CommandTemplateParser.Template_partContext):
        pass


    # Enter a parse tree produced by CommandTemplateParser#template_word.
    def enterTemplate_word(self, ctx:CommandTemplateParser.Template_wordContext):
        pass

    # Exit a parse tree produced by CommandTemplateParser#template_word.
    def exitTemplate_word(self, ctx:CommandTemplateParser.Template_wordContext):
        pass


    # Enter a parse tree produced by CommandTemplateParser#template_field.
    def enterTemplate_field(self, ctx:CommandTemplateParser.Template_fieldContext):
        pass

    # Exit a parse tree produced by CommandTemplateParser#template_field.
    def exitTemplate_field(self, ctx:CommandTemplateParser.Template_fieldContext):
        pass



del CommandTemplateParser