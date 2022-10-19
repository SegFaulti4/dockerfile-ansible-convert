from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Union, Type, Callable
from copy import deepcopy
import re

import dockerfile_ansible_convert.bash_parse as bash_parse
import dockerfile_ansible_convert._meta as _meta
import dockerfile_ansible_convert.commands_config as commands_config
from log import globalLog


@dataclass
class PatternToken:
    value: str

    def resolve(self, context: Dict[str, List[bash_parse.WordNode]]):
        raise NotImplementedError

    def match_word_node(self, node: bash_parse.WordNode):
        raise NotImplementedError

    def match_pattern_token(self, token):
        raise NotImplementedError

    def match(self, node):
        if isinstance(node, bash_parse.WordNode):
            return self.match_word_node(node)
        elif isinstance(node, PatternToken):
            return self.match_pattern_token(node)
        return None

    @staticmethod
    def from_str(s: str):
        if re.fullmatch(r'\[[^\[<\]>]+\.\.\.]', s):
            return AnyToken(value=s[1:-4])
        if re.fullmatch(r'[^\[<\]>]*<[^\[<\]>]+>', s):
            child = RequiredChildToken(value=re.search(r'<[^\[<\]>]+>', s).string[1:-1])
            prefix = s[:s.find('<')]
            return AbstractedToken(prefix=prefix, value=s, child=child)
        if re.fullmatch(r'[^\[<\]>]*\[[^\[<\]>]+]', s):
            child = OptionalChildToken(value=re.search(r'\[[^\[<\]>]+]', s).string[1:-1])
            prefix = s[:s.find('[')]
            return AbstractedToken(prefix=prefix, value=s, child=child)
        return ConstantToken(value=s)


@dataclass
class ChildToken:
    value: str


@dataclass
class OptionalChildToken(ChildToken):
    pass


@dataclass
class RequiredChildToken(ChildToken):
    pass


@dataclass
class ConstantToken(PatternToken):

    def resolve(self, context: Dict[str, List[bash_parse.WordNode]]):
        return bash_parse.WordNode(type=bash_parse.WordNode.Type.CONST, value=self.value, parts=list())

    def _match_value(self, value: str):
        if value == self.value:
            return dict()
        return None

    def match_word_node(self, node: bash_parse.WordNode):
        return self._match_value(node.value)

    def match_pattern_token(self, token: PatternToken):
        if isinstance(token, ConstantToken):
            return self._match_value(token.value)
        return None


@dataclass
class AbstractedToken(PatternToken):
    prefix: str
    child: ChildToken

    def resolve(self, context: Dict[str, List[bash_parse.WordNode]]):
        if self.value not in context or not context[self.value]:
            return None
        return concat_bash_word(prefix=self.prefix, word=context[self.value][0])

    def match_word_node(self, node: bash_parse.WordNode):
        if node.value.startswith(self.prefix):
            if node.value == self.prefix:
                if isinstance(self.child, OptionalChildToken):
                    return dict()
                return None
            cut_node = cut_bash_word(deepcopy(node), len(self.prefix))
            if cut_node is None:
                return None
            return {self.child.value: [cut_node]}
        return None

    def match_pattern_token(self, token: PatternToken):
        if isinstance(token, AnyToken):
            return None
        if token.value.startswith(self.prefix):
            if token.value == self.prefix:
                if isinstance(self.child, OptionalChildToken):
                    return dict()
                return None
            cut_token = cut_pattern_token(deepcopy(token), len(self.prefix))
            if cut_token is None:
                return None
            return {self.child.value: [cut_token]}
        return None


@dataclass
class AnyToken(PatternToken):

    def resolve(self, context: Dict[str, List[bash_parse.WordNode]]):
        if self.value not in context:
            return None
        return context[self.value]

    def match_word_node(self, node: bash_parse.WordNode):
        return {self.value: [deepcopy(node)]}

    def match_pattern_token(self, token: PatternToken):
        return {self.value: [deepcopy(token)]}


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
    params: Dict[str, List[bash_parse.WordNode]] = field(default_factory=dict)
    opts: Dict[str, List[bash_parse.WordNode]] = field(default_factory=dict)


@dataclass
class ShellExampleCall(CommandCallMixin):
    params: Dict[str, List[PatternToken]] = field(default_factory=dict)
    opts: Dict[str, List[PatternToken]] = field(default_factory=dict)


@dataclass
class CommandPattern(CommandCallMixin):
    tokens: List[PatternToken]

    @staticmethod
    def from_string(s: str, pattern_name: str, command_name: str):
        tokens = [PatternToken.from_str(p) for p in s.split()]
        return CommandPattern(pattern_name=pattern_name, tokens=tokens, command_name=command_name)


def concat_bash_word(prefix: str, word: bash_parse.WordNode):
    word.value = prefix + word.value
    for child in filter(lambda x: isinstance(x, bash_parse.ParameterNode), word.parts):
        child.pos = child.pos[0] + len(prefix), child.pos[1] + len(prefix)
    return word


def cut_bash_word(word: bash_parse.WordNode, start_pos: int):
    word.value = word.value[start_pos:]
    for child in filter(lambda x: isinstance(x, bash_parse.ParameterNode), word.parts):
        if child.pos[0] < start_pos:
            globalLog.debug("Can't cut parameterized word " + word.value)
            return None
        child.pos = child.pos[0] - start_pos, child.pos[1] - start_pos
    return word


def cut_pattern_token(token: PatternToken, start_pos: int):
    token.value = token.value[start_pos:]
    if isinstance(token, AbstractedToken):
        if len(token.prefix) < start_pos:
            return None
        token.prefix = token.prefix[start_pos:]
    elif isinstance(token, AnyToken):
        return None
    return token


def cut_general_word(word: Union[bash_parse.WordNode, PatternToken], start_pos: int):
    if isinstance(word, bash_parse.WordNode):
        return cut_bash_word(word, start_pos)
    elif isinstance(word, PatternToken):
        return cut_pattern_token(word, start_pos)
    return None


def merge_list_dicts(d1: Dict[str, List], d2: Dict[str, List]):
    for k, v in d2.items():
        if k not in d1:
            d1[k] = []
        d1[k].extend(v)


def merge_dicts(into_dict: Dict, from_dict: Dict):
    for k, v in from_dict.items():
        if k not in into_dict:
            into_dict[k] = deepcopy(v)
        else:
            if isinstance(v, Dict):
                if not isinstance(into_dict[k], Dict):
                    return None
                merge_dicts(into_dict[k], v)
            elif isinstance(v, List):
                if isinstance(into_dict[k], List):
                    into_dict[k].extend(deepcopy(v))
                else:
                    into_dict[k] = [into_dict[k]] + deepcopy(v)
            else:
                into_dict[k] = [into_dict[k]] + [deepcopy(v)]
    return into_dict


def visit_dict(d_dict: Dict, target: Type, target_func: Callable):
    queue = list((k, v, d_dict) for k, v in d_dict.items())
    visited = set()

    while queue:
        k, v, d = queue.pop(0)
        if isinstance(v, target):
            d[k] = target_func(v)
        elif isinstance(v, dict):
            if (id(k), id(d)) not in visited:
                queue.extend((_k, _v, v) for _k, _v in v.items())
        visited.add((id(k), id(d)))

    return d_dict


def match_token_list(tokens: List[PatternToken], words: List[Union[bash_parse.WordNode, PatternToken]], strict=False):
    t1 = list(t for t in tokens if isinstance(t, ConstantToken))
    t2 = sorted(list(t for t in tokens if isinstance(t, AbstractedToken)), key=lambda x: len(x.prefix))
    t3 = list(t for t in tokens if isinstance(t, AnyToken))
    t1.extend(t2)
    t1.extend(t3)

    res = {}
    for t in t1:
        if isinstance(t, AnyToken):
            if words:
                res[t.value] = deepcopy(words)
                words.clear()
        else:
            match_res = None
            for i, word in enumerate(words):
                match_res = t.match(word)
                if match_res is not None:
                    words.pop(i)
                    break

            if match_res is None:
                return None
            merge_list_dicts(res, match_res)

    if strict and words:
        return None
    return res


class ShellCommandParser:
    pattern: CommandPattern
    opts_map: Dict[str, CommandOpt]

    @dataclass
    class RT:
        opts: List = field(default_factory=list)
        params: Dict = field(default_factory=dict)
        skip_opts: bool = False
        words: List = field(default_factory=list)

    def __init__(self, pattern: CommandPattern, opts_map: Dict[str, CommandOpt] = None):
        if opts_map is None:
            opts_map = dict()
        self.pattern = pattern
        self.opts_map = opts_map
        self._rt = None

    def _parse(self, comm: List[Union[bash_parse.WordNode, PatternToken]]):
        self._rt = ShellCommandParser.RT(words=comm)

        for token in self.pattern.tokens:
            if not self._probe_token(token):
                self._rt = None
                return
        if not self._probe_opts():
            self._rt = None

    def parse(self, comm: List[Union[bash_parse.WordNode, PatternToken]]):
        self._parse(deepcopy(comm))
        res = None
        if self._rt is not None:
            if all(isinstance(word, bash_parse.WordNode) for word in comm):
                opts = self._group_opt_args()

                res = ShellCommandCall(command_name=self.pattern.command_name,
                                       pattern_name=self.pattern.pattern_name,
                                       params=self._rt.params,
                                       opts=opts)
            elif all(isinstance(token, PatternToken) for token in comm):
                opts = self._group_opt_args()

                res = ShellExampleCall(command_name=self.pattern.command_name,
                                       pattern_name=self.pattern.pattern_name,
                                       params=self._rt.params,
                                       opts=opts)
        self._rt = None
        return res

    def _match_token(self, token: PatternToken):
        if not token.value.startswith('-') and not self._probe_opts():
            return False
        if self._rt.words:
            match_res = token.match(self._rt.words.pop(0))
            if match_res is None:
                return False

            merge_list_dicts(self._rt.params, match_res)

            return True
        return True

    def _probe_token(self, token: PatternToken):
        if isinstance(token, AnyToken):
            while self._rt.words:
                if not self._match_token(token):
                    return False
            return True
        else:
            return self._match_token(token)

    def _probe_long(self):
        word = self._rt.words.pop(0)
        eq_pos = word.value.find('=')
        if eq_pos != -1:
            opt_name = word.value[:eq_pos]
            arg = cut_general_word(deepcopy(word), eq_pos + 1)
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
                globalLog.debug("Required arg is not provided for opt " + opt.name)
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
                    arg = cut_general_word(deepcopy(word), i + 1)
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
    def _match_command_field_by_example_field(example_field: Dict[str, Union[None, PatternToken, List[PatternToken]]],
                                              command_field: Dict[str, Union[None,
                                                                             bash_parse.WordNode,
                                                                             List[bash_parse.WordNode]]],
                                              strict: bool):
        res = {}
        for key, val in example_field.items():
            if key not in command_field:
                return None

            def listify_value(v):
                if v is None:
                    return []
                if not isinstance(v, list):
                    return [v]
                return v

            command_field[key] = listify_value(command_field[key])
            val = listify_value(val)
            comm_val = command_field[key]

            match_res = match_token_list(val, comm_val, strict=strict)
            if match_res is None:
                return None
            merge_list_dicts(res, match_res)
        return res

    @staticmethod
    def match_command_call_by_example(example: ShellExampleCall, comm_call: ShellCommandCall):
        res = {}
        match_res = ExampleBasedMatcher._match_command_field_by_example_field(example.params, comm_call.params, True)
        if match_res is None:
            return None
        merge_list_dicts(res, match_res)

        match_res = ExampleBasedMatcher._match_command_field_by_example_field(example.opts, comm_call.opts, False)
        if match_res is None:
            return None
        merge_list_dicts(res, match_res)

        return res

    @staticmethod
    def _resolve_module_call_pattern(module_call_pattern: Dict, context: Dict[str, List[bash_parse.WordNode]]):

        class Resolver:
            def __init__(self, context: Dict):
                self.context = context

            def __call__(self, token: PatternToken):
                return token.resolve(self.context)

        return visit_dict(module_call_pattern, PatternToken, Resolver(context))

    @staticmethod
    def postprocess_command_call_opts(comm_call: ShellCommandCall):
        conf_loader = CommandsConfigLoader()
        opts_postprocess = conf_loader.get_opts_postprocess_by_command_name(comm_call.command_name)
        opts_postprocess.sort(key=lambda x: len(x[0].opts), reverse=True)

        res = {}
        for opts_call, module_call_pattern in opts_postprocess:
            matching_call = deepcopy(comm_call)
            match_res = ExampleBasedMatcher._match_command_field_by_example_field(opts_call.opts,
                                                                                  matching_call.opts, False)
            if match_res is not None:
                module_call = ExampleBasedMatcher._resolve_module_call_pattern(module_call_pattern, match_res)
                merge_dicts(res, module_call)
                comm_call = matching_call

        return comm_call, res

    @staticmethod
    def _empty_command_call_field(command_field: Dict[str, List[bash_parse.WordNode]]):
        res = 0
        for v in command_field.values():
            if isinstance(v, list):
                res += len(v)
            else:
                res += 1

        return res == 0

    @staticmethod
    def _empty_command_call(comm_call: ShellCommandCall):
        return ExampleBasedMatcher._empty_command_call_field(comm_call.params) and \
               ExampleBasedMatcher._empty_command_call_field(comm_call.opts)

    @staticmethod
    def match_command_call(comm_call: ShellCommandCall):
        examples = CommandsConfigLoader().get_examples_by_pattern_name(comm_call.command_name, comm_call.pattern_name)

        for example, module_call_pattern in examples:
            matching_call = deepcopy(comm_call)
            match_res = ExampleBasedMatcher.match_command_call_by_example(example, matching_call)
            if match_res is not None:
                matching_call, opts_module_call = ExampleBasedMatcher.postprocess_command_call_opts(matching_call)
                if ExampleBasedMatcher._empty_command_call(matching_call):
                    main_module_call = ExampleBasedMatcher._resolve_module_call_pattern(module_call_pattern, match_res)
                    main_module_call = merge_dicts(main_module_call, opts_module_call)
                    return main_module_call
        return None

    @staticmethod
    def match_command(comm: List[bash_parse.WordNode]):
        if not ExampleBasedMatcher.is_allowed(comm):
            return None

        command_call = ExampleBasedMatcher.transform_to_command_call(comm)
        if command_call is None:
            return None
        return ExampleBasedMatcher.match_command_call(command_call)


class CommandsConfigLoader(metaclass=_meta.MetaSingleton):
    command_patterns_map: Dict[str, List[CommandPattern]] = dict()
    command_opts_map: Dict[str, Dict[str, CommandOpt]] = dict()
    command_example_map: Dict[str, Dict[str, List[Tuple[ShellExampleCall, Dict]]]] = dict()
    command_opts_postprocess_map: Dict[str, List[Tuple[ShellExampleCall, Dict]]] = dict()

    def __init__(self):
        for command_name in commands_config.match_config:
            command_config = commands_config.match_config[command_name]
            self.command_patterns_map[command_name] = list()
            self.command_opts_map[command_name] = dict()
            self.command_example_map[command_name] = dict()
            self.command_opts_postprocess_map[command_name] = list()

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
                self.command_example_map[command_name][pattern_name] = list()

            for example_str in command_config["examples"]:
                patterns, opts_map = self.command_patterns_map[command_name], self.command_opts_map[command_name]
                example = CommandPattern.from_string(example_str, command_name=command_name, pattern_name='')
                module_call_pattern = visit_dict(deepcopy(command_config["examples"][example_str]),
                                                 str, PatternToken.from_str)
                parsed = None

                for pattern in patterns:
                    parsed = ShellCommandParser(pattern=pattern, opts_map=opts_map).parse(example.tokens)
                    if parsed is not None:
                        break

                if parsed is None:
                    globalLog.warning("Failed to parse command example: " + example_str)
                else:
                    self.command_example_map[command_name][parsed.pattern_name].append((parsed, module_call_pattern))

            for opts_str in command_config["opts_postprocess_map"]:
                pattern = CommandPattern.from_string("[TRASH...]", command_name=command_name, pattern_name='opts postprocess')
                opts_map = self.command_opts_map[command_name]
                example = CommandPattern.from_string(opts_str, command_name=command_name, pattern_name='')
                module_call_pattern = visit_dict(deepcopy(command_config["opts_postprocess_map"][opts_str]),
                                                 str, PatternToken.from_str)
                parsed = ShellCommandParser(pattern=pattern, opts_map=opts_map).parse(example.tokens)

                if parsed is None:
                    globalLog.warning("Failed to parse postprocessing opts: " + opts_str)
                else:
                    self.command_opts_postprocess_map[command_name].append(
                        (parsed, module_call_pattern)
                    )

    def get_patterns_by_command_name(self, comm_name):
        return deepcopy(self.command_patterns_map[comm_name])

    def get_opts_map_by_command_name(self, comm_name):
        return deepcopy(self.command_opts_map[comm_name])

    def get_examples_by_pattern_name(self, command_name, pattern_name):
        return deepcopy(self.command_example_map[command_name][pattern_name])

    def get_opts_postprocess_by_command_name(self, command_name):
        return deepcopy(self.command_opts_postprocess_map[command_name])
