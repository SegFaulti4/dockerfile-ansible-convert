import bashlex
from bashlex.errors import ParsingError

from docker2ansible import exception
from docker2ansible.log import globalLog
import docker2ansible.dockerfile_ast.ast as ast
from dataclasses import dataclass, field


def parse_bash_value(bash_value):
    res = None
    try:
        res = bashlex.parse(bash_value)
        res = BashlexTransformer.simplify_nodes(res, bash_value)[0]
    except Exception as exc:
        globalLog.warning(type(exc))
        globalLog.warning(exc)
        globalLog.warning('Unexpected behavior while parsing value: ' + bash_value)
        res = ComplexValueNode(bash_value)
    finally:
        return res


def parse_bash(bash_line):
    parts = None
    res = []
    try:
        parts = bashlex.parse(bash_line)
        res = BashlexTransformer.transform_node(parts[0], bash_line)
    except exception.BashlexTransformException as exc:
        globalLog.info(exc)
        globalLog.info('Bashlex AST transform failed for AST: ' + str(parts))
    except (ParsingError, NotImplementedError) as exc:
        globalLog.info(exc)
        globalLog.info('Bash parsing failed for line: ' + bash_line)
    except Exception as exc:
        globalLog.warning(type(exc))
        globalLog.warning(exc)
        globalLog.warning('Unexpected behavior while parsing line: ' + bash_line)
    finally:
        return res


class BashlexTransformer:

    @staticmethod
    def simplify_nodes(bashlex_nodes, line):
        tr_node = BashlexTransformer.transform_node(bashlex_nodes[0], line)

        if len(bashlex_nodes) == 1 and bool(tr_node) and isinstance(tr_node[0], CommandNode) and \
                all(isinstance(child, PlainWordNode) for child in tr_node[0].children):
            return [ConstantValueNode(line)]
        elif len(bashlex_nodes) == 1 and bool(tr_node) and isinstance(tr_node[0], CommandNode) and \
                all(isinstance(child, PlainWordNode) or isinstance(child, ParameterizedWordNode)
                    for child in tr_node[0].children):
            return [ParameterizedValueNode(line,
                                           filter(lambda x: isinstance(x, ParameterizedWordNode), tr_node[0].children))]
        else:
            return [ComplexValueNode(line)]

    @staticmethod
    def transform_node(node, line):
        attr = getattr(BashlexTransformer, '_transform_' + node.kind, None)
        if attr is None:
            globalLog.info('Bashlex node kind "' + node.kind + '" is not supported')
        else:
            return attr(node, line)
        return []

    @staticmethod
    def _transform_list(node, line):
        res = []
        for part in node.parts:
            child = BashlexTransformer.transform_node(part, line)
            if not child:
                return []
            res.extend(filter(lambda x: not isinstance(x, EOCNode), child))

        return res

    @staticmethod
    def _transform_command(node, line):
        return [CommandNode(node, line)]

    @staticmethod
    def _transform_operator(node, line):
        if node.op == ';':
            return [EOCNode()]
        elif node.op == '&&':
            return [OperatorAndNode()]
        elif node.op == '||':
            return [OperatorOrNode()]

    @staticmethod
    def _transform_assignment(node, line):
        return [AssignmentNode(node, line)]

    @staticmethod
    def _transform_commandsubstitution(node, line):
        return [ComplexValueNode(line[node.pos[0]:node.pos[1]])]

    @staticmethod
    def _transform_parameter(node, line):
        return [ParameterNode(node, line)]

    @staticmethod
    def _transform_word(node, line):
        return [BashlexTransformer._classify_word_node(node)(node, line)]

    _PARAMETERIZED_WORD_CHILD_TYPES = {'parameter'}

    @staticmethod
    def _classify_word_node(node):
        if node.word[0] != '-':
            eq_pos = node.word.find('=')
            if eq_pos != -1 and all(x.pos[0] > eq_pos + node.pos[0] for x in node.parts):
                return AssignmentNode

            if eq_pos != -1:
                globalLog.info("Unexpected '=' symbol in word node " + node.dump())

        if len(node.parts):
            if all(map(lambda x: x in BashlexTransformer._PARAMETERIZED_WORD_CHILD_TYPES, node.parts)):
                return ParameterizedWordNode
            else:
                return WordSubstitutionNode
        else:
            return PlainWordNode


@dataclass
class Node(ast.Node):

    def _process(self):
        raise NotImplementedError


@dataclass
class CommandNode(Node):

    line = None

    def __init__(self, bashlex_node, line):
        self.line = line[bashlex_node.pos[0]:bashlex_node.pos[1]]
        for part in bashlex_node.parts:
            self.children.extend(BashlexTransformer.transform_node(part, line))

    def _process(self):
        pass

    def resolve(self):
        return self.stack.resolve_command(self)


@dataclass
class OperatorNode(Node):

    def _process(self):
        raise NotImplementedError


@dataclass
class OperatorAndNode(OperatorNode):

    def _process(self):
        pass


@dataclass
class OperatorOrNode(OperatorNode):

    def _process(self):
        pass


@dataclass
class EOCNode(Node):

    def _process(self):
        pass


@dataclass
class AssignmentNode(Node):

    name = None
    value = None

    def __init__(self, bashlex_node, line):
        eq_pos = bashlex_node.word.find('=')
        name, value = bashlex_node.word[0:eq_pos], bashlex_node.word[eq_pos + 1:]
        self.name = name
        self.value = value
        self.children.append(parse_bash_value(self.value))

    def _process(self):
        pass


@dataclass
class ParameterNode(Node):

    name = None
    pos = None

    def __init__(self, bashlex_node, line):
        self.name = bashlex_node.value
        self.pos = bashlex_node.pos

    def _process(self):
        pass


@dataclass
class WordNode(Node):

    value = None

    def __init__(self, bashlex_node, line):
        self.value = bashlex_node.word

    def _process(self):
        raise NotImplementedError


@dataclass
class PlainWordNode(WordNode):

    def __init__(self, bashlex_node, line):
        super().__init__(bashlex_node, line)

    def _process(self):
        pass


@dataclass
class ParameterizedWordNode(WordNode):

    value = None
    tracked = None
    resolvable = None

    def __init__(self, bashlex_node, line):
        super().__init__(bashlex_node, line)
        for part in bashlex_node.parts:
            part.pos = part.pos[0] - bashlex_node.pos[0], part.pos[1] - bashlex_node.pos[0]
            self.children.extend(BashlexTransformer.transform_node(part, line))

    def _process(self):
        pass


@dataclass
class WordSubstitutionNode(WordNode):

    value = None

    def __init__(self, bashlex_node, line):
        super().__init__(bashlex_node, line)
        for part in bashlex_node.parts:
            part.pos = part.pos[0] - bashlex_node.pos[0], part.pos[1] - bashlex_node.pos[0]
            self.children.extend(BashlexTransformer.transform_node(part, line))

    def _process(self):
        pass


@dataclass
class ValueNode(Node):

    value = None

    def __init__(self, value):
        self.value = value

    def _process(self):
        raise NotImplementedError


@dataclass
class ConstantValueNode(ValueNode):

    def __init__(self, value):
        super().__init__(value)

    def _process(self):
        pass


@dataclass
class ParameterizedValueNode(ValueNode):

    tracked = None
    resolvable = None

    def __init__(self, value, parameters):
        super().__init__(value)
        self.children = parameters
        self.tracked = all(self.stack.contains(x.name)
                           for x in filter(lambda x: isinstance(x, ParameterNode), self.children))
        self.resolvable = all(self.stack.resolvable(x.name)
                              for x in filter(lambda x: isinstance(x, ParameterNode), self.children))

    def _process(self):
        pass


@dataclass
class ComplexValueNode(ValueNode):

    def __init__(self, value):
        super().__init__(value)

    def _process(self):
        pass
