# Generated from /home/popovms/course/src/ansible_matcher/antlr/grammar/CommandTemplateParser.g4 by ANTLR 4.12.0
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .CommandTemplateParser import CommandTemplateParser
else:
    from CommandTemplateParser import CommandTemplateParser

# This class defines a complete generic visitor for a parse tree produced by CommandTemplateParser.

class CommandTemplateParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by CommandTemplateParser#command_template.
    def visitCommand_template(self, ctx:CommandTemplateParser.Command_templateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CommandTemplateParser#template_part.
    def visitTemplate_part(self, ctx:CommandTemplateParser.Template_partContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CommandTemplateParser#template_word.
    def visitTemplate_word(self, ctx:CommandTemplateParser.Template_wordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CommandTemplateParser#template_field.
    def visitTemplate_field(self, ctx:CommandTemplateParser.Template_fieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by CommandTemplateParser#template_postfix.
    def visitTemplate_postfix(self, ctx:CommandTemplateParser.Template_postfixContext):
        return self.visitChildren(ctx)



del CommandTemplateParser