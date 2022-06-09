from dataclasses import dataclass, field
from typing import List, Tuple, Dict
import re

import dockerfile_ansible_convert.bash_parse as bash_parse
import dockerfile_ansible_convert._meta as _meta
import dockerfile_ansible_convert.commands_config as commands_config
import exception
from log import globalLog


class TokenMatchResult(dict):
    pass


class PatternToken:

    def match(self, node: bash_parse.WordNode):
        raise NotImplementedError

    @staticmethod
    def from_str(s: str):
        if re.fullmatch(r'\[[^\[<\]>]+\.\.\.]', s):
            return AbstractionListToken(value=s[1:-4])
        if re.fullmatch(r'[^\[<\]>]*<[^\[<\]>]+>', s):
            child = RequiredChildToken(value=re.search(r'<[^\[<\]>]+>', s)[1:-1])
            prefix = s[:s.find('<')]
            return AbstractedToken(prefix=prefix, child=child)
        if re.fullmatch(r'[^\[<\]>]*\[[^\[<\]>]+]', s):
            child = OptionalChildToken(value=re.search(r'\[[^\[<\]>]+]', s)[1:-1])
            prefix = s[:s.find('[')]
            return AbstractedToken(prefix=prefix, child=child)
        return ConstantToken(value=s)


class ChildToken:
    pass


@dataclass
class OptionalChildToken(ChildToken):
    value: str


@dataclass
class RequiredChildToken(ChildToken):
    value: str


@dataclass
class ConstantToken(PatternToken):
    value: str

    def match(self, node: bash_parse.WordNode):
        if node.value == self.value:
            return TokenMatchResult()
        return None


@dataclass
class AbstractedToken(PatternToken):
    prefix: str
    child: ChildToken

    def match(self, node: bash_parse.WordNode):
        # TODO
        pass


@dataclass
class AbstractionListToken(PatternToken):
    value: str

    def match(self, node: bash_parse.WordNode):
        # TODO
        pass


@dataclass
class CommandOpt:
    arg_required: bool
    many_args: bool
    name: str


@dataclass
class CommandCallMixin:
    command_name: str
    pattern_name: str


@dataclass
class ShellCommandCall(CommandCallMixin):
    params: Dict[str, bash_parse.WordNode] = field(default_factory=dict)
    opts: Dict[str, bash_parse.WordNode] = field(default_factory=dict)


@dataclass
class ShellExampleCall(CommandCallMixin):
    params: Dict[str, PatternToken] = field(default_factory=dict)
    opts: Dict[str, PatternToken] = field(default_factory=dict)


@dataclass
class CommandPattern(CommandCallMixin):
    tokens: List[PatternToken]

    @staticmethod
    def from_string(s: str, pattern_name: str, command_name: str):
        tokens = [PatternToken.from_str(p) for p in s.split()]
        return CommandPattern(pattern_name=pattern_name, tokens=tokens, command_name=command_name)


def cut_bash_word(node: bash_parse.WordNode, start_pos: int):
    node.value = node.value[start_pos:]
    for child in filter(lambda x: isinstance(x, bash_parse.ParameterNode), node.parts):
        if child.pos[0] < start_pos:
            globalLog.debug("Can't cut parameterized word " + node.value)
            return None
        child.pos = child.pos[0] - start_pos, child.pos[1] - start_pos
    return node


class ShellCommandParser:
    pattern: CommandPattern
    opts_map: Dict[str, CommandOpt]

    @dataclass
    class RT:
        opts: List = field(default_factory=list)
        params: Dict = field(default_factory=list)
        skip_opts: bool = False
        words: List = field(default_factory=list)

    def __init__(self, pattern: CommandPattern, opts_map: Dict[str, CommandOpt] = None):
        if opts_map is None:
            opts_map = dict()
        self.pattern = pattern
        self.opts_map = opts_map
        self._rt = None

    def parse(self, comm: List[bash_parse.WordNode]):
        self._rt = ShellCommandParser.RT(words=comm)

        for token in self.pattern.tokens:
            if not self._probe_opts():
                return self._return_none()
            if self._rt.words:
                match_res = token.match(self._rt.words[0])
                if match_res is None:
                    return self._return_none()
                self._rt.params = {**self._rt.params, **match_res}
        if not self._probe_opts():
            return self._return_none()
        return self._return()

    def _probe_long(self):
        node = self._rt.words.pop(0)
        eq_pos = node.value.find('=')
        if eq_pos != -1:
            opt_name = node.value[:eq_pos]
            arg = cut_bash_word(node, eq_pos + 1)
        else:
            opt_name = node.value
            arg = None
        opt = self._opt_match(opt_name)
        if opt is None:
            return False
        if opt.arg_required and arg is None:
            if not self._rt.words or self._rt.words[0].value.startswith('-'):
                globalLog.debug("Required arg is not provided for opt " + opt.name)
                return False
            arg = self._rt.words.pop(0)
        self._rt.opts.append((opt, arg))
        return True

    def _probe_short(self):
        node = self._rt.words.pop(0)

        for i in range(1, len(node.value)):
            opt_name = node.value[i]
            opt = self._opt_match("-" + opt_name)
            if opt is None:
                return False

            if opt.arg_required:
                if node.value[i + 1:] != '':
                    arg = cut_bash_word(node, i + 1)
                    if arg is None:
                        return False
                else:
                    if not self._rt.words:
                        globalLog.debug("Required arg is not provided for opt " + opt.name)
                        return False
                    arg = self._rt.words.pop(0)
                self._rt.opts.append((opt, arg))
                break
            else:
                self._rt.opts.append((opt, None))
        return True

    def _probe_opts(self):
        while not self._rt.skip_opts and self._rt.words and \
                self._rt.words[0].value.startswith('-'):
            if self._rt.words[0].value == '--':
                self._rt_skip_opts = True
                self._rt.words.pop(0)
            else:
                if self._rt.words[0].value.startswith('--'):
                    if not self._probe_long():
                        return False
                else:
                    if not self._probe_short():
                        return False
        return True

    def _opt_match(self, opt_name):
        name_matches = [o for o in self.opts_map if o.startswith(opt_name)]
        if not name_matches:
            globalLog.debug("No matching opts found for " + opt_name)
            return None
        if opt_name in name_matches:
            return self.opts_map[opt_name]
        if len(name_matches) > 1:
            globalLog.debug("Too many matching opts for " + opt_name)
            return None
        return self.opts_map[name_matches[0]]

    def _return(self):
        opts = dict()
        for opt, arg in self._rt.opts:
            if opt.many_args:
                if opt.name not in opts:
                    opts[opt.name] = []
                opts[opt.name].append(arg)
            else:
                opts[opt.name] = arg

        res = ShellCommandCall(command_name=self.pattern.command_name,
                               pattern_name=self.pattern.pattern_name,
                               params=self._rt.params,
                               opts=opts)
        self._rt = None
        return res

    def _return_none(self):
        self._rt = None
        return None


class ExampleBasedMatcher:

    @staticmethod
    def transform_to_command_call(comm: List[bash_parse.WordNode]):
        patterns = CommandsConfigLoader().get_patterns_by_command_name(comm[0].value)
        opts_map = CommandsConfigLoader().get_opts_map_by_command_name(comm[0].value)
        res = None

        for pattern in patterns:
            res = ShellCommandParser(pattern=pattern, opts_map=opts_map).parse(comm)
            if res is not None:
                break
        return res

    @staticmethod
    def is_allowed(comm: List[bash_parse.WordNode]):
        return all(isinstance(part, bash_parse.WordNode) and part.type != bash_parse.WordNode.Type.COMPLEX
                   for part in comm) \
               and comm and comm[0].type == bash_parse.WordNode.Type.CONST

    @staticmethod
    def match_command_call_by_example(example: ShellExampleCall, comm_call: ShellCommandCall):
        # TODO
        return None

    @staticmethod
    def match_command_call(comm_call: ShellCommandCall):
        examples = CommandsConfigLoader().get_examples_by_pattern_name(comm_call.pattern_name)
        res = None

        for example in examples:
            res = ExampleBasedMatcher.match_command_call_by_example(example, comm_call)
            if res is not None:
                break
        return res

    @staticmethod
    def match_command(comm: List[bash_parse.WordNode]):
        if not ExampleBasedMatcher.is_allowed(comm):
            return None

        command_call = ExampleBasedMatcher.transform_to_command_call(comm)
        if command_call is None:
            return None
        return ExampleBasedMatcher.match_command_call(command_call)


class CommandsConfigLoader(metaclass=_meta.MetaSingleton):
    command_patterns_map: Dict[str, List[CommandPattern]]
    command_opts_map: Dict[str, Dict[str, CommandOpt]]

    def __init__(self):
        # TODO: use first word from pattern as a key for pattern mapping

        for command_name in commands_config.match_config:
            command_config = commands_config.match_config[command_name]
            self.command_patterns_map[command_name] = list()
            self.command_opts_map[command_name] = dict()

            for opt_name in command_config["opts"]:
                opt_config = command_config["opts"][opt_name]
                opt = CommandOpt(
                    name=opt_name,
                    arg_required=opt_config["arg_required"],
                    many_args=opt_config["many_args"]
                )

                for alias in opt_config["aliases"]:
                    self.command_opts_map[command_name][alias] = opt

            for pattern_name in command_config["patterns"]:
                for pattern_str in command_config["patterns"][pattern_name]:
                    self.command_patterns_map[command_name].append(
                        CommandPattern.from_string(pattern_str, pattern_name, command_name)
                    )

        # TODO: examples
        # TODO: opts_postprocess_map

    def get_patterns_by_command_name(self, comm_name):
        return self.command_patterns_map[comm_name]

    def get_opts_map_by_command_name(self, comm_name):
        return self.command_opts_map[comm_name]

    def get_examples_by_pattern_name(self, comm_name):
        # TODO
        return []


