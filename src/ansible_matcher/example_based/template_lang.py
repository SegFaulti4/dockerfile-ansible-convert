from src.ansible_matcher.example_based.antlr.src.CommandTemplateLexer import CommandTemplateLexer
from src.ansible_matcher.example_based.antlr.src.CommandTemplateParser import CommandTemplateParser
from src.ansible_matcher.example_based.antlr.src.CommandTemplateParserVisitor import CommandTemplateParserVisitor
from antlr4 import *
from typing import List, Union, Optional
from dataclasses import dataclass


@dataclass
class TemplateWord:
    word: str


@dataclass
class TemplateField:
    field_name: str
    spec_many: bool
    spec_optional: bool
    spec_path: bool


@dataclass
class TemplateObject:
    parts: List[Union[TemplateWord, TemplateField]]


@dataclass
class CommandTemplate:
    objects: List[TemplateObject]


class ConstructingTemplateVisitor(CommandTemplateParserVisitor):

    def visitCommand_template(self, ctx: CommandTemplateParser.Command_templateContext) -> Optional[CommandTemplate]:
        obj_contexts = ctx.template_object()
        if obj_contexts is None or not obj_contexts:
            return None

        objects = []
        for obj_ctx in obj_contexts:
            obj = self.visitTemplate_object(obj_ctx)
            if obj is None:
                return None
            objects.append(obj)

        return CommandTemplate(objects=objects)

    def visitTemplate_object(self, ctx: CommandTemplateParser.Template_objectContext) -> Optional[TemplateObject]:
        if ctx.children is None or not ctx.children:
            return None

        parts = []
        for child in ctx.getChildren():
            if isinstance(child, CommandTemplateParser.Template_wordContext):
                part = self.visitTemplate_word(child)
                if part is None:
                    return None
                parts.append(part)
            elif isinstance(child, CommandTemplateParser.Template_fieldContext):
                part = self.visitTemplate_field(child)
                if part is None:
                    return None
                parts.append(part)

        return TemplateObject(parts=parts)

    def visitTemplate_word(self, ctx: CommandTemplateParser.Template_wordContext) -> Optional[TemplateWord]:
        word = ctx.WORD()
        if word is None:
            return None
        return TemplateWord(word=word.getText())

    def visitTemplate_field(self, ctx: CommandTemplateParser.Template_fieldContext) -> Optional[TemplateField]:
        field_name = ctx.FIELD_NAME()
        if field_name is None:
            return None

        spec_many = ctx.SPEC_MANY() is not None
        spec_optional = ctx.SPEC_OPTIONAL() is not None
        spec_path = ctx.SPEC_PATH() is not None

        return TemplateField(field_name=field_name.getText(), spec_many=spec_many,
                             spec_optional=spec_optional, spec_path=spec_path)


if __name__ == "__main__":
    s = "rm -r {{ files : m }}"

    if False:
        data = InputStream(s)
        lexer = CommandTemplateLexer(data)
        stream = CommonTokenStream(lexer)
        stream.fill()
        tokens = stream.tokens

        print(s)
        print()
        for token in tokens:
            print(f'"{token.text}" \t{token.type} \t- \t{token.start} \t{token.stop}')

    data = InputStream(s)
    lexer = CommandTemplateLexer(data)
    stream = CommonTokenStream(lexer)
    parser = CommandTemplateParser(stream)
    tree = parser.command_template()
    visitor = ConstructingTemplateVisitor()
    template = visitor.visit(tree)

    print(s)
    print()
    print(template)
