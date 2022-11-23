import re
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
        res = []
        t = self.value[0:self.parts[0].pos[0]]
        if t:
            res.append(t)
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


@dataclasses.dataclass
class TemplateTweaks:
    cwd: str

    def tweak_spec_path(self, obj: Union[TemplatePart, ShellWordObject]):
        # TODO
        raise NotImplementedError


class CommandTemplateMatcher:
    template: CommandTemplateParts
    template_re: re.Pattern
    template_fields_dict: Dict[str, TemplateField]
    template_tweaks: Optional[TemplateTweaks]

    _RE_SHELL_PARAM_REPR = "α"
    _RE_SHELL_WORD_SEP = "ω"

    def __init__(self, template: CommandTemplateParts, template_tweaks: TemplateTweaks = None):
        self.template = template
        comm_re_str, fields = self._gen_command_template_re(template)
        self.template_re = re.compile(comm_re_str)
        self.template_fields_dict = {f.name: f for f in fields}
        self.template_tweaks = template_tweaks

    @staticmethod
    def _gen_template_field_re(template_field: TemplateField):
        # assuming that field_name is unique in current template
        return fr"(?P<field_{template_field.name}>.*)"

    @staticmethod
    def _gen_template_part_re(template_part: TemplatePart) -> Tuple[str, List[TemplateField]]:
        subpart_list = template_part.subpart_list()
        res_str = ""
        res_list = []

        many_flag = False

        for subpart in subpart_list:
            if isinstance(subpart, str):
                res_str += re.escape(subpart)
            elif isinstance(subpart, TemplateField):
                res_str += CommandTemplateMatcher._gen_template_field_re(subpart)
                res_list.append(subpart)
                many_flag = many_flag or subpart.spec_many

        if many_flag:
            res_str = f"({res_str})*"
        return res_str, res_list

    @staticmethod
    def _gen_command_template_re(command_template: CommandTemplateParts) -> Tuple[str, List[TemplateField]]:
        parts = [CommandTemplateMatcher._gen_template_part_re(part) for part in command_template]

        return fr"{CommandTemplateMatcher._RE_SHELL_WORD_SEP}".join(
            part[0] for part in parts
        ), [
                   f for part in parts for f in part[1]
               ]

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

    def match(self, obj: CommandCallParts) -> Optional[Dict[str, str]]:
        res = dict()
        command_str, command_params = self._preprocess_command(obj)
        match = self.template_re.fullmatch(command_str)

        params_slice_start = 0
        for key, value in match.groupdict().items():
            param_count = value.count(self._RE_SHELL_PARAM_REPR)
            constants = value.split(self._RE_SHELL_PARAM_REPR)

            field_name = key
            field_value = ""
            for constant, param in itertools.zip_longest(constants, command_params[params_slice_start:][:param_count]):
                if param is None:
                    field_value += constant
                else:
                    field_value += constant + param

            template_field = self.template_fields_dict[field_name]
            if template_field.spec_many:
                if field_name not in res:
                    res[field_name] = []
                res[field_name].append(field_value)
            else:
                res[key] = field_value
            params_slice_start += param_count

        for template_field in self.template_fields_dict.values():
            if not template_field.spec_optional:
                if template_field.name not in res:
                    globalLog.debug(f"Match failed - non optional field ({template_field.name}) doesn't have value")
                    return None
            if template_field.spec_path:
                if template_field in res:
                    if self.template_tweaks is None:
                        globalLog.debug(
                            f"Match warning - can't process path field ({template_field}), 'tweaks' is None")
                    else:
                        res[template_field.name] = self.template_tweaks.tweak_spec_path(res[template_field.name])

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
            -> Optional[ShellWordObject, TemplatePart]:

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
