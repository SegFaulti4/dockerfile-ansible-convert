import dataclasses
from typing import Optional, Union, Tuple, List, Dict

from src.shell.main import *
from src.ansible_matcher.template_lang import \
    TemplateField, TemplatePart, CommandCallParts, CommandTemplateParts, \
    CommandTemplateMatcher, TemplateTweaks, TemplateMatchResult
from src.ansible_matcher.utils import *

from src.log import globalLog


class Opt:
    name: str
    arg_required: bool
    many_args: bool
    aliases: List[str]

    def __init__(self, name: str, arg_req: bool, many_args: bool, aliases: List[str]):
        self.name = name
        self.arg_required = arg_req
        self.many_args = many_args
        self.aliases = aliases


CommandCallOpts = Dict[str, CommandCallParts]
CommandTemplateOpts = Dict[str, CommandTemplateParts]


@dataclasses.dataclass
class ExtractedCommandCall:
    params: CommandCallParts = dataclasses.field(default_factory=list)
    opts: CommandCallOpts = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class ExtractedCommandTemplate:
    params: CommandTemplateParts = dataclasses.field(default_factory=list)
    opts: CommandTemplateOpts = dataclasses.field(default_factory=dict)


class CommandOptsExtractor:
    opts_map: Dict[str, Opt]
    _rt = None

    @dataclasses.dataclass
    class RT:
        opts: List = dataclasses.field(default_factory=list)
        params: List = dataclasses.field(default_factory=list)
        words: List = dataclasses.field(default_factory=list)

    def __init__(self, opts_map: Optional[Dict[str, Opt]] = None):
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
                probe = self._probe_long()
            else:
                probe = self._probe_short()

            if probe is None:
                self._rt = None
                return
            if not probe:
                self._rt.params.append(word)
                self._rt.words.pop(0)

    def _probe_long(self) -> Optional[bool]:
        word = self._rt.words.pop(0)
        eq_pos = word.value.find('=')
        if eq_pos != -1:
            opt_name = word.value[:eq_pos]
            arg = self._cut_token(word, eq_pos + 1)
            if arg is None:
                return None
        else:
            opt_name = word.value
            arg = None

        opt = self._opt_match(opt_name)
        if opt is None:
            self._rt.words.insert(0, word)
            return False
        if opt.arg_required and arg is None:
            if not self._rt.words or self._rt.words[0].value.startswith('-'):
                globalLog.debug("Extraction failed - Required arg is not provided for opt " + opt.name)
                return None
            arg = self._rt.words.pop(0)
        self._rt.opts.append((opt, arg))
        return True

    def _probe_short(self) -> Optional[bool]:
        word = self._rt.words.pop(0)

        # try to match whole word as an option name (e.g. `gcc -dumpspecs`)
        opt = self._opt_match(word.value)
        if opt is not None:
            if not opt.arg_required:
                self._rt.opts.append((opt, None))
                return True
            if not self._rt.words:
                globalLog.debug("Extraction failed - Required arg is not provided for opt " + opt.name)
                return None
            arg = self._rt.words.pop(0)
            self._rt.opts.append((opt, arg))
            return True

        local_opts = []
        for i in range(1, len(word.value)):
            opt_name = word.value[i]
            opt = self._opt_match("-" + opt_name)
            if opt is None:
                self._rt.words.insert(0, word)
                return False

            if not opt.arg_required:
                local_opts.append((opt, None))
                continue

            if word.value[i + 1:] != '':
                arg = self._cut_token(word, i + 1)
                if arg is None:
                    return None
            else:
                if not self._rt.words:
                    globalLog.debug("Extraction failed - Required arg is not provided for opt " + opt.name)
                    return None
                arg = self._rt.words.pop(0)
            local_opts.append((opt, arg))
            break

        self._rt.opts.extend(local_opts)
        return True

    def _opt_match(self, opt_name) -> Optional[Opt]:
        name_matches = [o for o in self.opts_map if o.startswith(opt_name)]
        if opt_name in name_matches:
            return self.opts_map[opt_name]
        globalLog.debug(f"Couldn't find exact match for option {opt_name}")
        return None

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

    def _group_opt_args(self) \
            -> Dict[str, List[Union[ShellWordObject, TemplatePart]]]:
        opts = dict()
        for opt, arg in self._rt.opts:
            if opt.many_args:
                if opt.name not in opts:
                    opts[opt.name] = []
                opts[opt.name].append(arg)
            elif arg is None:
                opts[opt.name] = []
            else:
                opts[opt.name] = [arg]
        return opts


def match_extracted_call(extracted_call: ExtractedCommandCall, extracted_tmpl: ExtractedCommandTemplate,
                         template_tweaks: TemplateTweaks) -> Optional[Tuple[TemplateMatchResult, CommandCallOpts]]:
    params_matcher = CommandTemplateMatcher(template=extracted_tmpl.params, template_tweaks=template_tweaks)
    params_fields = params_matcher.full_match(extracted_call.params)
    if params_fields is None:
        return None

    opt_match = match_extracted_call_opts(extracted_call.opts, extracted_tmpl.opts, template_tweaks=template_tweaks)
    if opt_match is None:
        return None
    opt_fields, unmatched_opts = opt_match

    match_res = CommandTemplateMatcher.merge_match_results(params_fields, opt_fields)
    if match_res is None:
        return None

    return match_res, unmatched_opts


def match_extracted_call_opts(call_opts: CommandCallOpts, tmpl_opts: CommandTemplateOpts,
                              template_tweaks: TemplateTweaks) -> Optional[Tuple[TemplateMatchResult, CommandCallOpts]]:
    opt_fields = dict()
    unmatched_opts = {k: listify(v) for k, v in call_opts.items()}

    for k, v in tmpl_opts.items():
        if k not in call_opts:
            return None
        v = listify(v)

        if not v and not unmatched_opts[k]:
            del unmatched_opts[k]
            continue
        if not v or not unmatched_opts[k]:
            return None

        opt_matcher = CommandTemplateMatcher(template=v, template_tweaks=template_tweaks)
        opt_match = opt_matcher.match(call_opts[k])
        if opt_match is None:
            return None
        tmp_fields, unmatched = opt_match

        opt_fields = CommandTemplateMatcher.merge_match_results(opt_fields, tmp_fields)
        if opt_fields is None:
            return None

        if not unmatched:
            del unmatched_opts[k]
        else:
            unmatched_opts[k] = unmatched

    return opt_fields, unmatched_opts
