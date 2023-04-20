import dataclasses
from typing import Union, Optional, Dict

from src.shell.main import *
from src.ansible_matcher.template_lang import \
    TemplateField, TemplatePart, CommandCallParts, CommandTemplateParts

from src.log import globalLog


@dataclasses.dataclass
class CommandOpt:
    arg_required: bool
    many_args: bool
    name: str


@dataclasses.dataclass
class ExtractedCommandCall:
    params: CommandCallParts = dataclasses.field(default_factory=list)
    opts: Dict[str, CommandCallParts] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class ExtractedCommandTemplate:
    params: CommandTemplateParts = dataclasses.field(default_factory=list)
    opts: Dict[str, CommandTemplateParts] = dataclasses.field(default_factory=dict)


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

    def _opt_match(self, opt_name) -> Optional[CommandOpt]:
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
