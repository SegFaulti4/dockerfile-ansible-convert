import regex
import dataclasses
import itertools
import os
from src.ansible_matcher.antlr.src.CommandTemplateLexer import CommandTemplateLexer
from src.ansible_matcher.antlr.src.CommandTemplateParser import CommandTemplateParser
from src.ansible_matcher.antlr.src.CommandTemplateParserVisitor import CommandTemplateParserVisitor
from antlr4 import *
from typing import Union, Optional, Dict

from src.shell.main import *

from src.log import globalLog


@dataclasses.dataclass
class TemplateField:
    name: str
    pos: Tuple[int, int]
    spec_many: bool
    spec_optional: bool
    spec_path: bool


@dataclasses.dataclass
class TemplatePart:
    value: str
    parts: List[TemplateField]

    def subpart_list(self) -> List[Union[str, TemplateField]]:
        if not self.parts:
            return [self.value]

        res = []
        t = self.value[0:self.parts[0].pos[0]]
        if t:
            res.append(t)
        res.append(self.parts[0])
        cur_pos = self.parts[0].pos[1]

        for subpart in self.parts[1:]:
            res.append(self.value[cur_pos:subpart.pos[0]])
            res.append(subpart)
            cur_pos = subpart.pos[1]

        t = self.value[cur_pos:]
        if t:
            res.append(t)

        return res


CommandTemplateParts = List[TemplatePart]
CommandCallParts = List[ShellWordObject]


class TemplateConstructor(CommandTemplateParserVisitor):

    def from_str(self, template_str: str) -> Optional[CommandTemplateParts]:
        template_parser = CommandTemplateParser(
            CommonTokenStream(
                CommandTemplateLexer(
                    InputStream(template_str)
                )
            )
        )

        templ = template_parser.command_template()
        if not templ or not isinstance(templ, CommandTemplateParser.Command_templateContext):
            return None
        return self.visitCommand_template(templ)

    def visitCommand_template(self, ctx: CommandTemplateParser.Command_templateContext) \
            -> Optional[CommandTemplateParts]:
        obj_contexts = ctx.template_part()
        if obj_contexts is None or not obj_contexts:
            return None

        objects = []
        for obj_ctx in obj_contexts:
            if isinstance(obj_ctx, CommandTemplateParser.Template_partContext):
                obj = self.visitTemplate_part(obj_ctx)
                if obj is None:
                    return None
                objects.append(obj)
            else:
                return None

        return objects

    def visitTemplate_part(self, ctx: CommandTemplateParser.Template_partContext) -> Optional[TemplatePart]:
        if ctx.children is None or not ctx.children or \
                any(isinstance(c, ErrorNode) for c in ctx.getChildren()):
            return None

        template_part_value = ""
        template_part_parts = []
        for child in ctx.getChildren():
            if isinstance(child, CommandTemplateParser.Template_wordContext):
                part = self.visitTemplate_word(child)
                if part is None:
                    return None
                template_part_value += part
            elif isinstance(child, CommandTemplateParser.Template_fieldContext):
                part = self.visitTemplate_field(child)
                if part is None:
                    return None
                part[0].pos = part[0].pos[0] + len(template_part_value), part[0].pos[1] + len(template_part_value)
                template_part_parts.append(part[0])
                template_part_value += part[1]
            else:
                return None

        return TemplatePart(parts=template_part_parts, value=template_part_value)

    def visitTemplate_word(self, ctx: CommandTemplateParser.Template_wordContext) -> Optional[str]:
        return None if ctx.WORD() is None else ctx.WORD().getText()

    def visitTemplate_field(self, ctx: CommandTemplateParser.Template_fieldContext) \
            -> Optional[Tuple[TemplateField, str]]:
        if any(isinstance(c, ErrorNode) for c in ctx.getChildren()):
            return None

        token_open = ctx.OPEN()
        token_field_name = ctx.FIELD_NAME()
        token_spec_open = ctx.SPEC_OPEN()
        token_spec_many = ctx.SPEC_MANY()
        token_spec_optional = ctx.SPEC_OPTIONAL()
        token_spec_path = ctx.SPEC_PATH()
        token_close = ctx.CLOSE()

        def terminal_non_error(node):
            return isinstance(node, TerminalNode) and not isinstance(node, ErrorNode)

        if not terminal_non_error(token_open) or \
                not terminal_non_error(token_close) or \
                not terminal_non_error(token_field_name):
            return None

        def _token_txt(t):
            return "" if t is None else t.getText()

        field_repr = _token_txt(token_open) + _token_txt(token_field_name) + \
                     _token_txt(token_spec_open) + _token_txt(token_spec_many) + \
                     _token_txt(token_spec_optional) + _token_txt(token_spec_path) + \
                     _token_txt(token_close)

        return TemplateField(
            name=_token_txt(token_field_name),
            spec_many=token_spec_many is not None,
            spec_optional=token_spec_optional is not None,
            spec_path=token_spec_path is not None,
            pos=(0, len(field_repr))
        ), field_repr


@dataclasses.dataclass
class TemplateTweaks:
    cwd: str
    usr: str

    def tweak_spec_path(self, path: str):
        if path.startswith("/"):
            return path
        if path.startswith("~"):
            if self.usr is None:
                globalLog.info(f"Could not change path string - {path}, usr is None")
                return path
            if self.usr == "root":
                return os.path.join(f"/root/", path[1:])
            return os.path.join(f"/home/{self.usr}/", path[1:])

        if self.cwd is None:
            globalLog.info(f"Could not change path string - {path}, cwd is None")
            return path
        return os.path.join(self.cwd, path)


TemplateMatchResult = Dict[str, Union[str, List[str]]]


class CommandTemplateMatcher:
    template: CommandTemplateParts
    template_regex: regex.Pattern
    template_fields_dict: Dict[str, TemplateField]
    template_tweaks: Optional[TemplateTweaks]

    _RE_SHELL_PARAM_REPR = "α"
    _RE_SHELL_WORD_SEP = "ω"

    @staticmethod
    def merge_match_results(d1: TemplateMatchResult, d2: TemplateMatchResult) -> TemplateMatchResult:
        for k, v in d2.items():
            if isinstance(v, list):
                if k not in d1:
                    d1[k] = []
                d1[k].extend(v)
            else:
                d1[k] = v
        return d1

    def __init__(self, template: CommandTemplateParts, template_tweaks: TemplateTweaks = None):
        self.template = template
        comm_re_str, fields = self._gen_command_template_regex(template)
        self.template_regex = regex.compile(comm_re_str)
        self.template_fields_dict = {f.name: f for f in fields}
        self.template_tweaks = template_tweaks

    def match(self, obj: CommandCallParts) -> Optional[Tuple[TemplateMatchResult, CommandCallParts]]:
        command_str, command_params = self._preprocess_command(obj)

        match = self.template_regex.match(command_str)
        if match is None:
            return None

        field_values = self._extract_values(match, command_params)
        if field_values is None:
            return None

        unmatched_parts = self._unmatched_call_parts(match, obj, command_params, command_str)
        return field_values, unmatched_parts

    def full_match(self, obj: CommandCallParts) -> Optional[TemplateMatchResult]:
        command_str, command_params = self._preprocess_command(obj)

        match = self.template_regex.fullmatch(command_str)
        if match is None:
            return None

        return self._extract_values(match, command_params)

    @staticmethod
    def _gen_template_field_regex(template_field: TemplateField):
        # assuming that field_name is unique in current template
        return fr"(?P<field_{template_field.name}>[^{CommandTemplateMatcher._RE_SHELL_WORD_SEP}]*)"

    @staticmethod
    def _gen_template_part_regex(template_part: TemplatePart) -> Tuple[str, List[TemplateField], bool]:
        subpart_list = template_part.subpart_list()
        res_str = ""
        res_list = []

        many_flag = False

        for subpart in subpart_list:
            if isinstance(subpart, str):
                res_str += regex.escape(subpart)
            elif isinstance(subpart, TemplateField):
                res_str += CommandTemplateMatcher._gen_template_field_regex(subpart)
                res_list.append(subpart)
                many_flag = many_flag or subpart.spec_many

        return res_str, res_list, many_flag

    @staticmethod
    def _gen_command_template_regex(command_template: CommandTemplateParts) -> Tuple[str, List[TemplateField]]:
        sep = CommandTemplateMatcher._RE_SHELL_WORD_SEP
        res_str = ""
        res_list = []

        for part in command_template[:-1]:
            regex_str, field_list, many_flag = CommandTemplateMatcher._gen_template_part_regex(part)
            part_regex = f"{regex_str}{sep}"

            res_str += f"({part_regex})*" if many_flag else part_regex
            res_list.extend(field_list)

        last_str, last_list, last_flag = CommandTemplateMatcher._gen_template_part_regex(command_template[-1])
        res_str += f"({last_str}{sep})*({last_str})?" if last_flag else last_str
        res_list.extend(last_list)

        return res_str, res_list

    @staticmethod
    def _preprocess_shell_word(word: ShellWordObject) -> Tuple[str, List[str]]:
        res_str = ""
        res_list = []
        slice_start = 0

        for param in word.parts:
            res_str += word.value[slice_start:param.pos[0]]
            res_str += CommandTemplateMatcher._RE_SHELL_PARAM_REPR
            res_list.append(word.value[param.pos[0]:param.pos[1]])
            slice_start = param.pos[1]
        res_str += word.value[slice_start:]

        return res_str, res_list

    @staticmethod
    def _preprocess_command(obj: CommandCallParts) -> Tuple[str, List[str]]:
        preprocessed = [CommandTemplateMatcher._preprocess_shell_word(word) for word in obj]

        return CommandTemplateMatcher._RE_SHELL_WORD_SEP.join(
            prep[0] for prep in preprocessed
        ), [
            w for prep in preprocessed for w in prep[1]
        ]

    def _resolve_field_value(self, value: str, command_params: List[str], spec_path: bool = True) \
            -> Tuple[Optional[str], Optional[int]]:
        param_count = value.count(CommandTemplateMatcher._RE_SHELL_PARAM_REPR)
        constants = value.split(CommandTemplateMatcher._RE_SHELL_PARAM_REPR)

        if param_count > len(command_params):
            globalLog.debug("Match failed - not enough parameters to resolve field value")
            return None, None

        field_value = ""
        # don't need to handle the case when value starts with parameter
        # or when there is two or more parameters in a row
        # since corresponding constants returned by split() function will be ''
        for constant, param in itertools.zip_longest(constants, command_params[:param_count]):
            if param is None:
                field_value += constant
            else:
                field_value += constant + param

        if spec_path:
            # TODO: this looks dirty
            if not constants[0] or constants[0] == '"' or constants[0] == "'":
                globalLog.debug("Match info - path string starts with parameter, skipping handling")
            elif self.template_tweaks is None:
                globalLog.debug("Match warning - can't process path field, 'tweaks' is None")
            else:
                field_value = self.template_tweaks.tweak_spec_path(field_value)

        return field_value, param_count

    def _extract_values(self, match: regex.Match, comm_param_values: List[str]) -> Optional[Dict[str, str]]:
        res = dict()

        params_start = 0
        for field_name, field in self.template_fields_dict.items():
            captures = match.capturesdict().get(f"field_{field_name}", [])

            if not captures:
                if not field.spec_optional:
                    globalLog.debug(f"Match failed - non optional field ({field_name}) doesn't have value")
                    return None
                else:
                    continue

            if not field.spec_many:
                field_value, param_count = self._resolve_field_value(captures[-1], comm_param_values[params_start:],
                                                                     field.spec_path)
                if field_value is None:
                    return None
                res[field_name] = field_value
                params_start += param_count
            else:
                field_values = []
                for capture in captures:
                    field_value, param_count = self._resolve_field_value(capture, comm_param_values[params_start:],
                                                                         field.spec_path)
                    if field_value is None:
                        return None
                    field_values.append(field_value)
                    params_start += param_count
                res[field_name] = field_values

        return res

    @staticmethod
    def _unmatched_call_parts(match: regex.Match, comm: CommandCallParts,
                              comm_param_values: List[str], command_str: str) -> CommandCallParts:
        unmatched_str = command_str[match.span()[1]:]
        param_count = unmatched_str.count(CommandTemplateMatcher._RE_SHELL_PARAM_REPR)
        words = unmatched_str.split(CommandTemplateMatcher._RE_SHELL_WORD_SEP)

        comm_params = [param for word in comm for param in word.parts]

        res = []
        param_start = len(comm_params) - param_count
        for word in words:
            param_count = word.count(CommandTemplateMatcher._RE_SHELL_PARAM_REPR)
            consts = word.split(CommandTemplateMatcher._RE_SHELL_PARAM_REPR)

            value = ""
            parts = []
            for const, param_idx in itertools.zip_longest(consts, range(param_start, param_start + param_count)):
                value += const
                if param_idx is not None:
                    param = comm_params[param_idx]
                    param_value = comm_param_values[param_idx]
                    parts.append(ShellParameterObject(
                        name=param.name,
                        pos=(len(value), len(value) + len(param_value))
                    ))
                    value += param_value

            if value:
                res.append(ShellWordObject(value=value, parts=parts))

        return res


class TemplateFiller:
    template: TemplatePart

    def __init__(self, templ: CommandTemplateParts):
        value = templ[0].value
        parts = templ[0].parts

        for part in templ[1:]:
            value += " "
            for f in part.parts:
                parts.append(TemplateField(name=f.name, pos=(f.pos[0] + len(value), f.pos[1] + len(value)),
                                           spec_many=False, spec_optional=False, spec_path=False))
        self.template = TemplatePart(value=value, parts=parts)

    def fill(self, fields_dict: TemplateMatchResult, strict: bool = False) -> Optional[Union[str, List[str]]]:
        res_size = 0
        single_value_fields = []
        list_values_fields = []
        for f in self.template.parts:
            if f.name not in fields_dict and strict:
                return None
            if isinstance(fields_dict[f.name], list):
                if res_size == 0:
                    res_size = len(fields_dict[f.name])
                elif res_size != len(fields_dict[f.name]):
                    return None
                list_values_fields.append(f.name)
            else:
                single_value_fields.append(f.name)

        if res_size == 0:
            return TemplateFiller.fill_single_values(self.template, fields_dict, strict)
        else:
            res = []
            values_dict = {f: fields_dict[f] for f in single_value_fields}
            for i in range(res_size):
                for f in list_values_fields:
                    values_dict[f] = fields_dict[f][i]
                res.append(TemplateFiller.fill_single_values(self.template, values_dict, strict))
                if res[-1] is None:
                    return None
            return res

    @staticmethod
    def fill_single_values(templ_part: TemplatePart, values_dict: Dict[str, str], strict: bool) -> Optional[str]:
        res = ""
        for subpart in templ_part.subpart_list():
            if isinstance(subpart, str):
                res += subpart
            elif isinstance(subpart, TemplateField):
                if subpart.name not in values_dict:
                    if strict:
                        return None
                    else:
                        res += templ_part.value[subpart.pos[0]:subpart.pos[1]]

                res += values_dict[subpart.name]
        return res


if __name__ == "__main__":
    from dev.sandbox.shell.main import SandboxShellParser

    shell_parser = SandboxShellParser()
    template_constr = TemplateConstructor()

    c_s = "rm -rf ./a.c ~/b.c"
    t_s = "rm -rf {{ files : m }}"
    command = shell_parser.parse(c_s)[0]
    template = TemplateConstructor().from_str(t_s)

    matcher = CommandTemplateMatcher(template)
    res = matcher.match(command.parts)

    print(t_s)
    print()
    print(template)
    print()
    print(res)
