import regex
import dataclasses
import itertools
from src.ansible_matcher.antlr.src.CommandTemplateLexer import CommandTemplateLexer
from src.ansible_matcher.antlr.src.CommandTemplateParser import CommandTemplateParser
from src.ansible_matcher.antlr.src.CommandTemplateParserVisitor import CommandTemplateParserVisitor
from src.utils import path_utils
from antlr4 import *
from typing import Union, Optional, Dict

from src.shell.main import *

from src.log import globalLog


@dataclasses.dataclass
class TemplateField:
    name: str
    pos: Tuple[int, int]
    spec_many: bool
    spec_no_wildcards: bool
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
TemplateMatchResult = Dict[str, Union[str, List[str]]]


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

        # we need to check that whole string was parsed as command template
        if not templ \
                or not isinstance(templ, CommandTemplateParser.Command_templateContext) \
                or templ.stop.stop != len(template_str) - 1:
            return None
        return self.visitCommand_template(templ)
        # TODO: check that all duplicate fields have same options

    def visitCommand_template(self, ctx: CommandTemplateParser.Command_templateContext) \
            -> Optional[CommandTemplateParts]:
        parts = ctx.template_part()
        if parts is None or not parts:
            return None

        objects = []
        for part_ctx in parts:
            if isinstance(part_ctx, CommandTemplateParser.Template_partContext):
                obj = self.visitTemplate_part(part_ctx)
            else:
                obj = None
            if obj is None:
                return None
            objects.append(obj)

        prefix = ctx.template_postfix()
        if prefix is not None:
            obj = self.visitTemplate_postfix(prefix)
            if obj is None:
                return None
            objects.append(obj)

        return objects

    def visitTemplate_postfix(self, ctx: CommandTemplateParser.Template_postfixContext) -> Optional[TemplatePart]:
        return None if ctx.SPACE() is None else TemplatePart(parts=[], value="")

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
        token_spec_no_wildcards = ctx.SPEC_NO_WILDCARDS()
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

        field_repr = \
            _token_txt(token_open) + \
            _token_txt(token_field_name) + \
            _token_txt(token_spec_open) + \
            _token_txt(token_spec_many) + \
            _token_txt(token_spec_no_wildcards) + \
            _token_txt(token_spec_optional) + \
            _token_txt(token_spec_path) + \
            _token_txt(token_close)

        return TemplateField(
            name=_token_txt(token_field_name),
            spec_many=token_spec_many is not None,
            spec_no_wildcards=token_spec_no_wildcards is not None,
            spec_optional=token_spec_optional is not None,
            spec_path=token_spec_path is not None,
            pos=(0, len(field_repr))
        ), field_repr


def tmpl_c(s: str) -> Optional[CommandTemplateParts]:
    return TemplateConstructor().from_str(s)


@dataclasses.dataclass
class TemplateTweaks:
    cwd: str
    usr: str

    def tweak_spec_path(self, path: str):
        return path_utils.path_str_wrapper(path, cwd=self.cwd, usr=self.usr)

    # TODO: (not so soon) delegate wildcard recognition to shell parser
    @staticmethod
    def has_wildcards(value: str) -> bool:
        # TODO: add support for brackets
        return "*" in value or "?" in value


class CommandTemplateMatcher:
    template: CommandTemplateParts
    template_regex: regex.Pattern
    template_fields_dict: Dict[str, TemplateField]
    template_tweaks: Optional[TemplateTweaks]

    _RE_SHELL_PARAM_REPR = "α"
    _RE_SHELL_WORD_SEP = "ω"

    @staticmethod
    def merge_match_results(d1: TemplateMatchResult, d2: TemplateMatchResult) -> Optional[TemplateMatchResult]:
        for k, v in d2.items():
            if k in d1:
                globalLog.debug("Couldn't merge match results - found two values for the same key")
                return None
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
    def _gen_template_part_regex(template_part: TemplatePart) -> Tuple[str, List[TemplateField], bool, bool]:
        subpart_list = template_part.subpart_list()
        res_str = ""
        res_list = []

        many_flag = False
        optional_flag = False

        for subpart in subpart_list:
            if isinstance(subpart, str):
                res_str += regex.escape(subpart)
            elif isinstance(subpart, TemplateField):
                res_str += CommandTemplateMatcher._gen_template_field_regex(subpart)
                res_list.append(subpart)
                many_flag = many_flag or subpart.spec_many
                optional_flag = optional_flag or subpart.spec_optional

        return res_str, res_list, many_flag, optional_flag

    @staticmethod
    def _gen_command_template_regex(command_template: CommandTemplateParts) -> Tuple[str, List[TemplateField]]:
        sep = CommandTemplateMatcher._RE_SHELL_WORD_SEP
        res_str = ""
        res_list = []

        for part in command_template:
            regex_str, field_list, many_flag, optional_flag = CommandTemplateMatcher._gen_template_part_regex(part)
            part_regex = f"{regex_str}{sep}"

            part_regex = f"({part_regex})*" if many_flag else part_regex
            part_regex = f"({part_regex})?" if optional_flag else part_regex

            res_str += part_regex
            res_list.extend(field_list)

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
        ) + CommandTemplateMatcher._RE_SHELL_WORD_SEP, [
            w for prep in preprocessed for w in prep[1]
        ]

    def _resolve_field_value(self, value: str, command_params: List[str], spec_path: bool, spec_no_wildcards: bool) \
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
        if spec_no_wildcards and TemplateTweaks.has_wildcards(field_value):
            globalLog.debug("Match failed - found wildcards")
            return None, None

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
                                                                     field.spec_path, field.spec_no_wildcards)
                if field_value is None:
                    return None
                res[field_name] = field_value
                params_start += param_count
            else:
                field_values = []
                for capture in captures:
                    field_value, param_count = self._resolve_field_value(capture, comm_param_values[params_start:],
                                                                         field.spec_path, field.spec_no_wildcards)
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
    template: CommandTemplateParts

    def __init__(self, templ: CommandTemplateParts):
        assert all(isinstance(p, TemplatePart) for p in templ)
        self.template = templ

    @staticmethod
    def _fill_template_part(part: TemplatePart, values_dict: Dict[str, str]) -> str:
        res = ""
        for subpart in part.subpart_list():
            if isinstance(subpart, str):
                res += subpart
            elif isinstance(subpart, TemplateField):
                res += values_dict.get(subpart.name, "")
        return res

    @staticmethod
    def _get_multiples(fields_dict: TemplateMatchResult, field_names: List[str]) \
            -> List[int]:
        return list(set(len(fields_dict[name]) for name in field_names
                        if name in fields_dict and isinstance(fields_dict[name], list)))

    def fill_flatten(self, fields_dict: TemplateMatchResult, strict: bool = False) -> Optional[str]:
        res = []
        for part in self.template:
            field_names = list(f.name for f in part.parts)
            if any(name not in fields_dict for name in field_names) and strict:
                return None
            multiples = TemplateFiller._get_multiples(fields_dict, field_names)

            if not multiples:
                values_dict = {name: fields_dict[name] for name in field_names if name in fields_dict}
                res.append(TemplateFiller._fill_template_part(part, values_dict))
            elif len(multiples) > 1:
                globalLog.debug("Found multiple different sized lists in fields dict - filling failed")
                return None
            elif multiples[0] == 0 and strict:
                return None
            else:
                values = []
                for i in range(multiples[0]):
                    values_dict = {}
                    for name in field_names:
                        if name not in fields_dict:
                            continue
                        if isinstance(fields_dict[name], list):
                            values_dict[name] = fields_dict[name][i]
                        else:
                            values_dict[name] = fields_dict[name]
                    values.append(TemplateFiller._fill_template_part(part, values_dict))
                res.append(" ".join(values))

        return " ".join(res)

    def fill_expand(self, fields_dict: TemplateMatchResult, strict: bool = False) -> Optional[List[str]]:
        res = []
        field_names = list(f.name for part in self.template for f in part.parts)
        if any(name not in fields_dict for name in field_names) and strict:
            return None
        multiples = TemplateFiller._get_multiples(fields_dict, field_names)

        if not multiples:
            values_dict = {name: fields_dict[name] for name in field_names if name in fields_dict}
            res.append(" ".join(TemplateFiller._fill_template_part(part, values_dict) for part in self.template))
        elif len(multiples) > 1:
            globalLog.debug("Found multiple different sized lists in fields dict - filling failed")
            return None
        elif multiples[0] == 0 and strict:
            return None
        else:
            for i in range(multiples[0]):
                values_dict = {}
                for name in field_names:
                    if name not in fields_dict:
                        continue
                    if isinstance(fields_dict[name], list):
                        values_dict[name] = fields_dict[name][i]
                    else:
                        values_dict[name] = fields_dict[name]
                res.append(" ".join(TemplateFiller._fill_template_part(part, values_dict) for part in self.template))
        return res
