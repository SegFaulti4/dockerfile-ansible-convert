from bashlex.errors import ParsingError

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple, Dict
import bashlex

import dockerfile_ansible_convert._meta as _meta
import dockerfile_ansible_convert.enrich_config
import exception
from log import globalLog


def parse_bash_commands(line):
    res = []
    try:
        commands = bashlex.parse(line)
        res = BashlexTransformer.transform_commands(commands, line)
    except (ParsingError, NotImplementedError) as exc:
        globalLog.info(exc)
        globalLog.info('Bash parsing with bashlex failed for line: ' + line)
    except Exception as exc:
        globalLog.warning(type(exc))
        globalLog.warning(exc)
        globalLog.warning('Unexpected behavior while parsing line: ' + line)
    finally:
        return res


def parse_bash_value(value):
    res = None
    try:
        if not value.startswith('"') or not value.endswith('"'):
            value = '"' + value + '"'
        nodes = bashlex.parse(value)
        res = BashlexTransformer.transform_value(nodes, value)
    except Exception as exc:
        globalLog.warning(type(exc))
        globalLog.warning(exc)
        globalLog.warning('Unexpected behavior while parsing value: ' + value)
        res = BashlexTransformer.bogus_value(value)
    finally:
        return res


class BashlexTransformer:

    @staticmethod
    def bogus_value(line):
        return WordNode(parts=[], type=WordNode.Type.COMPLEX, value=line)

    @staticmethod
    def transform_value(nodes, line):
        if len(nodes) != 1 or not nodes[0].parts:
            return BashlexTransformer.bogus_value(line)

        parts = []
        for part in nodes[0].parts:
            child = BashlexTransformer._transform_node(part, line)
            if isinstance(child[0], UnsupportedNode) or not isinstance(child[0], WordNode) or child[0].type == WordNode.Type.COMPLEX:
                return BashlexTransformer.bogus_value(line)
            parts.extend(child)

        if all(x.type == WordNode.Type.CONST for x in parts):
            return WordNode(parts=[], type=WordNode.Type.CONST, value=line)

        value = ""
        params = []
        for part in parts:
            if part.type == WordNode.Type.PARAMETERIZED:
                for param in part.parts:
                    param.pos = param.pos[0] + len(value), param.pos[1] + len(value)
                    params.append(param)
            value += part.value + ' '

        return WordNode(parts=params, type=WordNode.Type.PARAMETERIZED, value=value)

    @staticmethod
    def transform_commands(commands, line):
        res = []
        for node in commands:
            tmp = BashlexTransformer._transform_node(node, line)
            if not isinstance(tmp[0], UnsupportedNode):
                res.extend(tmp)

        return res

    @staticmethod
    def _transform_node(node, line):
        attr = getattr(BashlexTransformer, '_transform_' + node.kind, None)
        if attr is None:
            globalLog.info('Bashlex node kind "' + node.kind + '" is not supported')
        else:
            return attr(node, line)
        return [UnsupportedNode()]

    @staticmethod
    def _transform_list(node, line):
        res = []
        for part in node.parts:
            child = BashlexTransformer._transform_node(part, line)
            if isinstance(child[0], UnsupportedNode):
                child = [CommandNode(parts=[], line=line[part.pos[0]:part.pos[1]])]
            res.extend(filter(lambda x: not isinstance(x, _EOCNode), child))

        return res

    @staticmethod
    def _transform_command(node, line):
        comm_line = line[node.pos[0]:node.pos[1]]
        parts = []
        for part in node.parts:
            transformed = BashlexTransformer._transform_node(part, line)
            if isinstance(transformed[0], UnsupportedNode):
                return [CommandNode(parts=[], line=comm_line)]
            parts.extend(transformed)

        if len(parts) == 2 and all(isinstance(p, WordNode) for p in parts) and parts[0].value == "export":
            second_part = parse_bash_commands(node.parts[1].word)
            if len(second_part) == 1 and isinstance(second_part[0], AssignmentNode):
                return second_part

        if len(parts) == 1 and isinstance(parts[0], AssignmentNode):
            return [parts[0]]

        res = CommandNode(parts=parts, line=comm_line)
        #enriched = BashEnricher().enrich_command(res)
        #if enriched is None:
        #    res.parts.clear()
        #else:
        #    res = enriched
        return [res]

    @staticmethod
    def _transform_operator(node, line):
        if node.op == ';':
            return [_EOCNode(parts=[])]
        elif node.op == '&&':
            return [OperatorAndNode(parts=[])]
        elif node.op == '||':
            return [OperatorOrNode(parts=[])]

    @staticmethod
    def _transform_assignment(node, line):
        eq_pos = node.word.find('=')
        name, value = node.word[0:eq_pos], node.word[eq_pos + 1:]

        part = parse_bash_value(value)

        return [AssignmentNode(parts=[part], name=name)]

    @staticmethod
    def _transform_commandsubstitution(node, line):
        return [BashlexTransformer.bogus_value(line[node.pos[0]:node.pos[1]])]

    @staticmethod
    def _transform_parameter(node, line):
        return [ParameterNode(parts=[], name=node.value, pos=(node.pos[0] - 1, node.pos[1]))]

    @staticmethod
    def _transform_word(node, line):
        if len(node.parts):
            parts = []
            for part in node.parts:
                parts.extend(BashlexTransformer._transform_node(part, line))
            parts = [p for p in parts if not isinstance(p, TildeNode)]
            if not parts:
                return [WordNode(parts=[], type=WordNode.Type.CONST, value=node.word)]
            if all(isinstance(p, ParameterNode) for p in parts):
                for p in parts:
                    p.pos = p.pos[0] - node.pos[0], p.pos[1] - node.pos[0]
                return [WordNode(parts=parts, type=WordNode.Type.PARAMETERIZED, value=node.word)]
            return [WordNode(parts=[], type=WordNode.Type.COMPLEX, value=node.word)]
        else:
            return [WordNode(parts=[], type=WordNode.Type.CONST, value=node.word)]

    @staticmethod
    def _transform_tilde(node, line):
        return [TildeNode(parts=[])]


class BashEnricher(metaclass=_meta.MetaSingleton):
    _scenarios = {}
    _opts = []
    _map_opts = {}

    def __init__(self):
        """
        {
            command_name: {
                "opts": {
                    "name": {
                        "arg_required": bool,
                        "many_args": bool,
                        "aliases": [
                            str,
                            ...
                        ]
                    },
                    ...
                },
                "scenarios": {
                    "name": {
                        "aliases": [
                            str,
                            ...
                        ]
                    }
                }
            }
            ...
        }
        """
        config = dockerfile_ansible_convert.enrich_config.commands
        for command_name in config:
            self._map_opts[command_name] = {}
            for opt_name in config[command_name]["opts"]:
                opt = config[command_name]["opts"][opt_name]
                new_opt = BashEnricher._CommandScenario.Opt(
                    name=opt_name,
                    arg_required=opt["arg_required"],
                    many_args=opt["many_args"]
                )
                for alias in opt["aliases"]:
                    self._map_opts[command_name][alias] = new_opt
                self._opts.append(new_opt)
            self._scenarios[command_name] = []
            for scenario_name in config[command_name]["scenarios"]:
                scenario = config[command_name]["scenarios"][scenario_name]
                for alias in scenario["aliases"]:
                    requires = []
                    for req_str in alias.split():
                        if req_str.startswith('<') and req_str.endswith('>'):
                            requires.append(BashEnricher._CommandScenario.Req(
                                type=BashEnricher._CommandScenario.Req.Type.STRICT_ABSTRACT,
                                value=req_str[1:-1]
                            ))
                        elif req_str.startswith('[') and req_str.endswith('...]'):
                            requires.append(BashEnricher._CommandScenario.Req(
                                type=BashEnricher._CommandScenario.Req.Type.OPTIONAL_ABSTRACT_LIST,
                                value=req_str[1:-4]
                            ))
                        elif req_str.startswith('[') and req_str.endswith(']'):
                            requires.append(BashEnricher._CommandScenario.Req(
                                type=BashEnricher._CommandScenario.Req.Type.OPTIONAL_ABSTRACT,
                                value=req_str[1:-1]
                            ))
                        else:
                            requires.append(BashEnricher._CommandScenario.Req(
                                type=BashEnricher._CommandScenario.Req.Type.STRICT_CONSTANT,
                                value=req_str
                            ))
                    self._scenarios[command_name].append(BashEnricher._CommandScenario(
                        command_name=command_name,
                        scenario_name=scenario_name,
                        requires=requires,
                        map_opts=self._map_opts[command_name]
                    ))

    @staticmethod
    def _is_allowed(comm):
        return isinstance(comm, CommandNode) and all(isinstance(part, WordNode) and part.type != WordNode.Type.COMPLEX
                                                     for part in comm.parts) \
               and comm.parts and comm.parts[0].type == WordNode.Type.CONST

    def enrich_command(self, comm):
        if BashEnricher._is_allowed(comm):
            command_name = comm.parts[0].value
            for scenario in self._scenarios.get(command_name, []):
                res = scenario.probe(comm)
                if res is not None:
                    return res
            globalLog.info("Suitable scenario not found for command " + comm.line)
        return None

    @dataclass(repr=False)
    class _CommandScenario:
        command_name: str
        scenario_name: str
        requires: List
        map_opts: Dict

        _rt_result = None
        _rt_comm_list = None
        _rt_require = None
        _rt_skip_opts = None
        _rt_opts = None

        @dataclass(repr=False)
        class Req:

            class Type(Enum):
                STRICT_CONSTANT = "strict_constant"
                STRICT_ABSTRACT = "strict_abstract"
                OPTIONAL_ABSTRACT = "optional_abstract"
                OPTIONAL_ABSTRACT_LIST = "optional_abstract_list"

            type: Type
            value: str

        @dataclass(repr=False)
        class Opt:
            arg_required: bool
            many_args: bool
            name: str

        def probe(self, comm):
            try:
                self._rt_result = CommandNode(parts=[], line=comm.line, name=self.command_name,
                                              fullname=self.scenario_name)
                self._rt_comm_list = comm.parts.copy()
                self._rt_skip_opts = False
                self._rt_opts = []

                for require in self.requires:
                    self._rt_require = require
                    getattr(self, "_probe_" + require.type.value)()

                self._probe_opts()

                # if self._rt_comm_list:
                #     raise exception.EnrichCommandException('Excessive arguments provided')
                return self._return()

            except AttributeError as exc:
                globalLog.warning(exc)
                globalLog.warning("Unknown Req type for scenario " + self.scenario_name)
                self._rt_result = None
                return self._return()
            except ValueError as exc:
                globalLog.info(exc)
                self._rt_result = None
                return self._return()
            except KeyError as exc:
                globalLog.info(exc)
                self._rt_result = None
                return self._return()
            except exception.EnrichCommandException as exc:
                globalLog.info(exc)
                globalLog.info(comm.line)
                self._rt_result = None
                return self._return()

        def _return(self):
            if self._rt_result is not None:
                for opt, arg in self._rt_opts:
                    if opt.many_args:
                        if opt.name not in self._rt_result.opts:
                            self._rt_result.opts[opt.name] = []
                        self._rt_result.opts[opt.name].append(arg)
                    else:
                        self._rt_result.opts[opt.name] = arg

            self._rt_comm_list = []
            self._rt_require = None
            self._rt_skip_opts = False
            self._rt_opts = []
            return self._rt_result

        def _probe_strict_constant(self):
            self._probe_opts()
            if self._rt_comm_list:
                node = self._rt_comm_list[0]
                if isinstance(node, WordNode) and node.type == WordNode.Type.CONST \
                        and node.value == self._rt_require.value:
                    self._rt_comm_list.pop(0)
                    return
            raise exception.EnrichCommandException("Strict constant Req " + self._rt_require.value +
                                                   " is not satisfied")

        def _probe_strict_abstract(self):
            self._probe_opts()
            if self._rt_comm_list:
                self._rt_result.params[self._rt_require.value] = self._rt_comm_list.pop(0)
                return
            raise exception.EnrichCommandException("Strict abstract Req " + self._rt_require.value +
                                                   " is not satisfied")

        def _probe_optional_abstract(self):
            self._probe_opts()
            if self._rt_comm_list:
                self._rt_result.params[self._rt_require.value] = self._rt_comm_list.pop(0)

        def _probe_optional_abstract_list(self):
            while self._rt_comm_list:
                self._probe_opts()
                if self._rt_comm_list:
                    if self._rt_require.value not in self._rt_result.params:
                        self._rt_result.params[self._rt_require.value] = []
                    self._rt_result.params[self._rt_require.value].append(self._rt_comm_list.pop(0))

        def _probe_opts(self):
            while not self._rt_skip_opts and self._rt_comm_list and \
                    self._rt_comm_list[0].value.startswith('-'):
                if self._rt_comm_list[0].value == '--':
                    self._rt_skip_opts = True
                    self._rt_comm_list.pop(0)
                else:
                    if self._rt_comm_list[0].value.startswith('--'):
                        self._probe_long()
                    else:
                        self._probe_short()

        def _probe_long(self):
            node = self._rt_comm_list.pop(0)
            eq_pos = node.value.find('=')
            if eq_pos != -1:
                opt_name = node.value[:eq_pos]
                arg = self._cut_bash_word(node, eq_pos + 1)
            else:
                opt_name = node.value
                arg = None
            opt = self._opt_match(opt_name)

            if opt.arg_required:
                if arg is None:
                    if not self._rt_comm_list or self._rt_comm_list[0].value.startswith('-'):
                        exception.EnrichCommandException("Required arg is not provided for opt " + opt.name)
                    arg = self._rt_comm_list.pop(0)
            self._rt_opts.append((opt, arg))

        def _probe_short(self):
            node = self._rt_comm_list.pop(0)

            for i in range(1, len(node.value)):
                opt_name = node.value[i]
                opt = self._opt_match("-" + opt_name)
                if opt.arg_required:
                    if node.value[i + 1:] != '':
                        arg = self._cut_bash_word(node, i + 1)
                    else:
                        if not self._rt_comm_list:
                            raise exception.EnrichCommandException("Required arg is not provided for opt " + opt.name)
                        arg = self._rt_comm_list.pop(0)
                    self._rt_opts.append((opt, arg))
                    break
                else:
                    self._rt_opts.append((opt, None))

        def _cut_bash_word(self, node, start_pos):
            node.value = node.value[start_pos:]
            for child in filter(lambda x: isinstance(x, ParameterNode), node.parts):
                if child.pos[0] < start_pos:
                    raise exception.EnrichCommandException("Can't cut parameterized word")
                child.pos = child.pos[0] - start_pos, child.pos[1] - start_pos
            return node

        def _opt_match(self, opt_name):
            name_matches = [o for o in self.map_opts if o.startswith(opt_name)]
            if not name_matches:
                raise exception.EnrichCommandException("No matching opts found")
            if opt_name in name_matches:
                return self.map_opts[opt_name]
            if len(name_matches) > 1:
                raise exception.EnrichCommandException("Too many matching opts for " + opt_name)
            return self.map_opts[name_matches[0]]


class NodeEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


@dataclass
class Node:
    parts: List

    #def __repr__(self):
    #    return json.dumps(self, indent=4, sort_keys=True, cls=NodeEncoder)


class UnsupportedNode(Node):
    def __init__(self):
        pass


@dataclass(repr=False)
class CommandNode(Node):
    line: str
    name: str = None
    fullname: str = None
    params: Dict = field(default_factory=dict)
    opts: Dict = field(default_factory=dict)


class OperatorAndNode(Node):
    pass


class OperatorOrNode(Node):
    pass


class TildeNode(Node):
    pass


@dataclass(repr=False)
class AssignmentNode(Node):
    name: str


@dataclass(repr=False)
class ParameterNode(Node):
    name: str
    pos: Tuple


@dataclass(repr=False)
class WordNode(Node):
    class Type(Enum):
        CONST = "const"
        PARAMETERIZED = "parameterized",
        COMPLEX = "complex"

    type: Type
    value: str

    #@property
    #def __dict__(self):
    #    return {"type": self.type.value, "value": self.value, "parts": self.parts}

class _EOCNode(Node):
    pass
