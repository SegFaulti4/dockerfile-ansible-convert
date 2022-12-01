import regex
import dataclasses
import itertools
from src.ansible_matcher.example_based.antlr.src.CommandTemplateLexer import CommandTemplateLexer
from src.ansible_matcher.example_based.antlr.src.CommandTemplateParser import CommandTemplateParser
from src.ansible_matcher.example_based.antlr.src.CommandTemplateParserVisitor import CommandTemplateParserVisitor
from antlr4 import *
from typing import List, Union, Optional, Dict

from src.ansible_matcher.main import *
from src.shell.main import *
from src.ansible_matcher.example_based.commands_config import match_config
from src.utils.meta import MetaSingleton

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

    def subpart_list(self):
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
        if templ is None or not isinstance(templ, CommandTemplateParser.Command_templateContext):
            return None
        return self.visitCommand_template(templ)

    def visitCommand_template(self, ctx: CommandTemplateParser.Command_templateContext) \
            -> Optional[CommandTemplateParts]:
        obj_contexts = ctx.template_part()
        if obj_contexts is None or not obj_contexts:
            return None

        objects = []
        for obj_ctx in obj_contexts:
            obj = self.visitTemplate_part(obj_ctx)
            if obj is None:
                return None
            objects.append(obj)

        return objects

    def visitTemplate_part(self, ctx: CommandTemplateParser.Template_partContext) -> Optional[TemplatePart]:
        if ctx.children is None or not ctx.children:
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

        return TemplatePart(parts=template_part_parts, value=template_part_value)

    def visitTemplate_word(self, ctx: CommandTemplateParser.Template_wordContext) -> Optional[str]:
        return None if ctx.WORD() is None else ctx.WORD().getText()

    def visitTemplate_field(self, ctx: CommandTemplateParser.Template_fieldContext) \
            -> Optional[Tuple[TemplateField, str]]:

        token_open = ctx.OPEN()
        token_field_name = ctx.FIELD_NAME()
        token_spec_open = ctx.SPEC_OPEN()
        token_spec_many = ctx.SPEC_MANY()
        token_spec_optional = ctx.SPEC_OPTIONAL()
        token_spec_path = ctx.SPEC_PATH()
        token_close = ctx.CLOSE()

        if token_open is None or token_close is None or token_field_name is None:
            return None

        def _token_txt(t):
            return "" if t is None else t.getText()

        field_repr = _token_txt(token_open) + _token_txt(token_field_name) + _token_txt(token_spec_open) + \
            _token_txt(token_spec_many) + _token_txt(token_spec_optional) + _token_txt(token_spec_path) + \
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

    def tweak_spec_path(self, path: str):
        # TODO
        raise NotImplementedError


class CommandTemplateMatcher:
    template: CommandTemplateParts
    template_regex: regex.Pattern
    template_fields_dict: Dict[str, TemplateField]
    template_tweaks: Optional[TemplateTweaks]

    _RE_SHELL_PARAM_REPR = "α"
    _RE_SHELL_WORD_SEP = "ω"

    def __init__(self, template: CommandTemplateParts, template_tweaks: TemplateTweaks = None):
        self.template = template
        comm_re_str, fields = self._gen_command_template_regex(template)
        self.template_regex = regex.compile(comm_re_str)
        self.template_fields_dict = {f.name: f for f in fields}
        self.template_tweaks = template_tweaks

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
        res_str = "^"
        res_list = []

        for part in command_template[:-1]:
            regex_str, field_list, many_flag = CommandTemplateMatcher._gen_template_part_regex(part)
            part_regex = f"{regex_str}{sep}"

            res_str += f"({part_regex})*" if many_flag else part_regex
            res_list.extend(field_list)

        last_str, last_list, last_flag = CommandTemplateMatcher._gen_template_part_regex(command_template[-1])
        res_str += f"({last_str}{sep})*({last_str})?" if last_flag else last_str
        res_str += "$"
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

    def _resolve_field_value(self, value: str, command_params: List[str], spec_path: bool) \
            -> Tuple[Optional[str], Optional[int]]:
        param_count = value.count(CommandTemplateMatcher._RE_SHELL_PARAM_REPR)
        constants = value.split(CommandTemplateMatcher._RE_SHELL_PARAM_REPR)

        if param_count > len(command_params):
            globalLog.debug("Match failed - not enough parameters to resolve field value")
            return None, None

        field_value = ""
        for constant, param in itertools.zip_longest(constants, command_params[:param_count]):
            if param is None:
                field_value += constant
            else:
                field_value += constant + param

        if spec_path:
            if self.template_tweaks is None:
                globalLog.debug("Match warning - can't process path field, 'tweaks' is None")
            else:
                field_value = self.template_tweaks.tweak_spec_path(field_value)

        return field_value, param_count

    def match(self, obj: CommandCallParts) -> Optional[Dict[str, str]]:
        res = dict()
        command_str, command_params = self._preprocess_command(obj)
        match = self.template_regex.fullmatch(command_str)

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
                field_value, param_count = self._resolve_field_value(captures[-1], command_params[params_start:],
                                                                     field.spec_path)
                if field_value is None:
                    return None
                res[field_name] = field_value
                params_start += param_count
            else:
                field_values = []
                for capture in captures:
                    field_value, param_count = self._resolve_field_value(capture, command_params[params_start:],
                                                                         field.spec_path)
                    if field_value is None:
                        return None
                    field_values.append(field_value)
                    params_start += param_count
                res[field_name] = field_values

        return res


@dataclasses.dataclass
class CommandOpt:
    arg_required: bool
    many_args: bool
    name: str


@dataclasses.dataclass
class ExtractedCommandCall:
    params: CommandCallParts = dataclasses.field(default_factory=list)
    opts: Dict[str, List[ShellWordObject]] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class ExtractedCommandTemplate:
    params: CommandTemplateParts = dataclasses.field(default_factory=list)
    opts: Dict[str, List[TemplatePart]] = dataclasses.field(default_factory=dict)


class CommandOptsExtractor:
    opts_map: Dict[str, CommandOpt]
    _rt = None

    @dataclasses.dataclass
    class RT:
        opts: List = dataclasses.field(default_factory=list)
        params: List = dataclasses.field(default_factory=list)
        words: List = dataclasses.field(default_factory=list)
        
    def __init__(self, opts_map: Optional[Dict[str, CommandOpt]] = None):
        if opts_map is None:
            opts_map = dict()
        self.opts_map = opts_map

    def extract(self, comm: Union[CommandCallParts, CommandTemplateParts]) \
            -> Optional[Union[ExtractedCommandCall, ExtractedCommandTemplate]]:

        self._extract(comm)
        res = None

        if self._rt is not None:
            if all(isinstance(word, ShellWordObject) for word in comm):
                opts = self._group_opt_args()
                res = ExtractedCommandCall(params=self._rt.params,
                                           opts=opts)

            elif all(isinstance(part, TemplatePart) for part in comm):
                opts = self._group_opt_args()
                res = ExtractedCommandTemplate(params=self._rt.params,
                                               opts=opts)

        self._rt = None
        return res

    def _extract(self, comm: Union[CommandCallParts, CommandTemplateParts]):
        self._rt = CommandOptsExtractor.RT(words=comm)

        while self._rt.words:
            word = self._rt.words[0]

            if not word.value.startswith('-'):
                self._rt.params.append(word)
                self._rt.words.pop(0)
                continue

            if word.value == '--':
                self._rt.params.extend(self._rt.words[1:])
                self._rt.words.clear()
                break

            if word.value.startswith('--'):
                if not self._probe_long():
                    self._rt = None
                    return
            else:
                if not self._probe_short():
                    self._rt = None
                    return

    def _probe_long(self):
        word = self._rt.words.pop(0)
        eq_pos = word.value.find('=')
        if eq_pos != -1:
            opt_name = word.value[:eq_pos]
            arg = self._cut_token(word, eq_pos + 1)
            if arg is None:
                return False
        else:
            opt_name = word.value
            arg = None

        opt = self._opt_match(opt_name)
        if opt is None:
            return False
        if opt.arg_required and arg is None:
            if not self._rt.words or self._rt.words[0].value.startswith('-'):
                globalLog.debug("Extraction failed - Required arg is not provided for opt " + opt.name)
                return False
            arg = self._rt.words.pop(0)
        self._rt.opts.append((opt, arg))
        return True

    def _probe_short(self):
        word = self._rt.words.pop(0)

        for i in range(1, len(word.value)):
            opt_name = word.value[i]
            opt = self._opt_match("-" + opt_name)
            if opt is None:
                return False

            if opt.arg_required:
                if word.value[i + 1:] != '':
                    arg = self._cut_token(word, i + 1)
                    if arg is None:
                        return False
                else:
                    if not self._rt.words:
                        globalLog.debug("Extraction failed - Required arg is not provided for opt " + opt.name)
                        return False
                    arg = self._rt.words.pop(0)
                self._rt.opts.append((opt, arg))
                break
            else:
                self._rt.opts.append((opt, None))
        return True

    def _opt_match(self, opt_name):
        name_matches = [o for o in self.opts_map if o.startswith(opt_name)]
        if not name_matches:
            globalLog.debug("Extraction failed - No matching opts found for " + opt_name)
            return None
        if opt_name in name_matches:
            return self.opts_map[opt_name]
        if len(name_matches) > 1:
            globalLog.debug("Extraction failed - Too many matching opts for " + opt_name)
            return None
        return self.opts_map[name_matches[0]]

    @staticmethod
    def _cut_token(token: Union[ShellWordObject, TemplatePart], start_pos: int) \
            -> Optional[Union[ShellWordObject, TemplatePart]]:

        if isinstance(token, ShellWordObject):
            part_type = ShellParameterObject
            err_msg = f"Extraction failed - can't cut shell word - {token.value}"
        elif isinstance(token, TemplatePart):
            part_type = TemplateField
            err_msg = f"Extraction failed - can't cut template part - {token.value}"
        else:
            return None

        token.value = token.value[start_pos:]
        for part in filter(lambda x: isinstance(x, part_type), token.parts):
            if part.pos[0] < start_pos:
                globalLog.debug(err_msg)
                return None
            part.pos = part.pos[0] - start_pos, part.pos[1] - start_pos
        return token

    def _group_opt_args(self):
        opts = dict()
        for opt, arg in self._rt.opts:
            if opt.many_args:
                if opt.name not in opts:
                    opts[opt.name] = []
                opts[opt.name].append(arg)
            else:
                opts[opt.name] = arg
        return opts


if __name__ == "__main__":
    from sandbox.shell_parser.main import SandboxShellParser

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
