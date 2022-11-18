from src.ansible_matcher.example_based.antlr.src.CommandTemplateLexer import CommandTemplateLexer
from src.ansible_matcher.example_based.antlr.src.CommandTemplateParser import CommandTemplateParser
from src.ansible_matcher.example_based.antlr.src.CommandTemplateParserVisitor import CommandTemplateParserVisitor
from antlr4 import *
from typing import List, Union, Optional, Dict
from dataclasses import dataclass, field
from itertools import zip_longest

from src.ansible_matcher.main import *
from src.shell.main import *
from src.ansible_matcher.example_based.commands_config import match_config
from src.utils.meta import MetaSingleton

from src.log import globalLog


@dataclass
class TemplateField:
    name: str
    pos: Tuple[int, int]
    spec_many: bool
    spec_optional: bool
    spec_path: bool


@dataclass
class TemplatePart:
    value: str
    parts: List[TemplateField]


CommandTemplate = List[TemplatePart]
Command = List[ShellWordObject]


@dataclass
class TemplateTweaks:
    cwd: str

    def tweak_spec_path(self, obj: Union[TemplatePart, ShellWordObject]):
        # TODO
        raise NotImplementedError


class CommandTemplateMatcher:
    ObjectPart = Union[TemplatePart, ShellWordObject]
    Object = Union[CommandTemplate, Command]

    template: CommandTemplate
    template_tweaks: Optional[TemplateTweaks]
    _cur: Optional[TemplatePart]

    def __init__(self, template: CommandTemplate, template_tweaks: TemplateTweaks = None):
        self.template = template
        self.template_tweaks = template_tweaks

    @staticmethod
    def _cut_object_part(part: ObjectPart, start_pos: int, end_pos: int) -> ObjectPart:
        raise NotImplementedError

    @staticmethod
    def _subpart_list(part: TemplatePart) -> List[Union[str, TemplateField]]:
        subpart_list = []
        t = part.value[0:part.parts[0].pos[0]]
        if t:
            subpart_list.append(t)
        cur_pos = part.parts[0].pos[1]

        for subpart in part.parts[1:]:
            subpart_list.append(part.value[cur_pos:subpart.pos[0]])
            subpart_list.append(subpart)
            cur_pos = subpart.pos[1]

        t = part.value[cur_pos:]
        if t:
            subpart_list.append(t)

        return subpart_list

    def match_object(self, obj: Object):
        raise NotImplementedError

    # TODO: refactor as class
    def _match_object_part(self, obj_part: ObjectPart) -> Optional[Dict[str, Union[ObjectPart, List[ObjectPart]]]]:
        if self._cur is None:
            return None

        many_flag = False
        match_dict = dict()
        subpart_list = self._subpart_list(self._cur)
        obj_pos = 0
        obj_idx = 0

        def handle_field(field: TemplateField, start_pos: int, end_pos: int) -> bool:
            nonlocal many_flag
            nonlocal match_dict

            # spec_optional behavior
            if start_pos == end_pos:
                if not field.spec_optional:
                    globalLog.debug("Can't allow empty non optional template field")
                    return False
                return True

            field_name = field.name
            field_value = self._cut_object_part(obj_part, start_pos, end_pos)

            # spec_path behavior
            if field.spec_path:
                if self.template_tweaks is None:
                    globalLog.debug("Skipping spec_path handling")
                else:
                    field_value = self.template_tweaks.tweak_spec_path(field_value)

            # spec_many behavior
            if field.spec_many:
                many_flag = True
                if field_name not in match_dict or not isinstance(match_dict[field_name], list):
                    match_dict[field_name] = []
                match_dict[field_name].append(field_value)
            else:
                match_dict[field_name] = field_value

            return True

        for sub_a, sub_b in zip_longest(subpart_list, subpart_list[1:]):
            if sub_b is None:
                if isinstance(sub_a, str):
                    start_pos = obj_pos
                    if obj_idx < len(obj_part.parts):
                        globalLog.debug("Can't match abstract subpart with constant string")
                        return None
                    else:
                        end_pos = len(obj_part.value)

                    if len(sub_a) > end_pos - start_pos:
                        globalLog.debug("Not enough chars at the end of matching part to match constant string")
                        return None
                    if not obj_part.value[start_pos:end_pos].startswith(sub_a):
                        globalLog.debug("Constant strings don't match")
                        return None

                elif isinstance(sub_a, TemplateField):
                    start_pos = obj_pos
                    end_pos = len(obj_part.value)

                    if not handle_field(sub_a, start_pos, end_pos):
                        return None

            elif isinstance(sub_a, str) and isinstance(sub_b, TemplateField):
                start_pos = obj_pos
                if obj_idx < len(obj_part.parts):
                    end_pos = obj_part.parts[obj_idx].pos[0]
                else:
                    end_pos = len(obj_part.value)

                if len(sub_a) > end_pos - start_pos:
                    globalLog.debug("Not enough chars to match constant string")
                    return None
                if not obj_part.value[start_pos:end_pos].startswith(sub_a):
                    globalLog.debug("Constant strings don't match")
                    return None
                obj_pos += len(sub_a)

            elif isinstance(sub_a, TemplateField) and isinstance(sub_b, str):
                start_pos = obj_pos
                end_pos = -1
                end_idx = obj_idx

                cur_pos = obj_pos
                for subpart in obj_part.parts[obj_idx:]:
                    if sub_b in obj_part.value[cur_pos:subpart.pos[0]]:
                        end_pos = cur_pos + obj_part.value[cur_pos:subpart.pos[0]].find(sub_b) + len(sub_b)
                        break
                    cur_pos = subpart.pos[1]
                    end_idx += 1

                if end_pos == -1:
                    if sub_b in obj_part.value[cur_pos:]:
                        end_pos = cur_pos + obj_part.value[cur_pos:].find(sub_b) + len(sub_b)
                    else:
                        globalLog.debug("Couldn't find constant string")
                        return None

                if not handle_field(sub_a, start_pos, end_pos):
                    return None

                obj_pos = end_pos
                obj_idx = end_idx

        if not many_flag:
            self._cur = None

        return match_dict


@dataclass
class CommandOpt:
    arg_required: bool
    many_args: bool
    name: str


@dataclass
class SubcommandMixin:
    command_name: str
    subcommand_name: str


@dataclass
class ExtractedCommandCall(SubcommandMixin):
    params: Dict[str, List[ShellWordObject]] = field(default_factory=dict)
    opts: Dict[str, List[ShellWordObject]] = field(default_factory=dict)


@dataclass
class ExtractedCommandExample(SubcommandMixin):
    params: Dict[str, List[TemplatePart]] = field(default_factory=dict)
    opts: Dict[str, List[TemplatePart]] = field(default_factory=dict)


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
