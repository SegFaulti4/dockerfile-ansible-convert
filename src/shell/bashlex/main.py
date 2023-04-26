import bashlex
import bashlex.ast

from src.shell.main import *
from src.log import globalLog

from typing import List, Union


class BashlexNodeTransformer:

    @staticmethod
    def transform_node(node: bashlex.ast.node, line: str) -> List[ShellObject]:
        attr = getattr(BashlexNodeTransformer, 'transform_' + node.kind, None)
        if attr is None:
            globalLog.info('Bashlex node kind "' + node.kind + '" is not supported')
        else:
            return attr(node, line)
        return []

    @staticmethod
    def transform_list(node: bashlex.ast.node, line: str) -> List[ShellObject]:
        res = []
        for part in node.parts:
            child = BashlexNodeTransformer.transform_node(part, line)
            if not child:
                child = [ShellRawObject(value=line[part.pos[0]:part.pos[1]])]
            res.extend(child)
        return res

    @staticmethod
    def transform_command(node: bashlex.ast.node, line) \
            -> List[Union[ShellRawObject, ShellAssignmentObject, ShellCommandObject]]:

        comm_line = line[node.pos[0]:node.pos[1]]
        parts = []
        for part in node.parts:
            child = BashlexNodeTransformer.transform_node(part, line)
            if not child:
                return [ShellRawObject(value=comm_line)]
            parts.extend(child)

        # check for export assignment
        # if len(parts) == 2 and all(isinstance(p, WordNode) for p in parts) and parts[0].value == "export":
        #    second_part = parse_bash_commands(node.parts[1].word)
        #    if len(second_part) == 1 and isinstance(second_part[0], AssignmentNode):
        #        return second_part

        # check for assignment
        if len(parts) == 1 and isinstance(parts[0], ShellAssignmentObject):
            return [parts[0]]

        if ShellCommandObject.allowed_parts(parts):
            obj = ShellCommandObject(parts=parts, line=comm_line)
        else:
            obj = ShellRawObject(value=comm_line)
        return [obj]

    @staticmethod
    def transform_operator(node: bashlex.ast.node, line: str) -> List[ShellOperatorObject]:
        if node.op == ';':
            return [ShellOperatorEndObject()]
        elif node.op == '&&':
            return [ShellOperatorAndObject()]
        elif node.op == '||':
            return [ShellOperatorOrObject()]

    @staticmethod
    def transform_assignment(node: bashlex.ast.node, line: str) -> List[ShellAssignmentObject]:
        eq_pos = node.word.find('=')
        name, value = node.word[0:eq_pos], node.word[eq_pos + 1:]

        # workaround to preserve literal values
        # not sure if it's still needed
        if not value.startswith('"') or not value.endswith('"'):
            value = '"' + value + '"'
        # Circular dependency
        part = BashlexShellParser().parse_as_expression(value)
        return [ShellAssignmentObject(name=name, value=part)]

    @staticmethod
    def transform_commandsubstitution(node: bashlex.ast.node, line: str) -> List[ShellRawObject]:
        return [ShellRawObject(value=line[node.pos[0]:node.pos[1]])]

    @staticmethod
    def transform_parameter(node: bashlex.ast.node, line: str) -> List[ShellParameterObject]:
        return [ShellParameterObject(name=node.value, pos=(node.pos[0], node.pos[1]))]

    @staticmethod
    def transform_word(node, line) -> List[Union[ShellWordObject, ShellRawObject]]:
        parts = []
        word_line = line[node.pos[0]:node.pos[1]]
        for part in node.parts:
            part.pos = part.pos[0] - node.pos[0], part.pos[1] - node.pos[0]
            parts.extend(BashlexNodeTransformer.transform_node(part, line))
        if ShellWordObject.allowed_parts(parts):
            return [ShellWordObject(value=word_line, parts=parts)]
        return [ShellRawObject(value=word_line)]

    @staticmethod
    def transform_tilde(node, line):
        return []


class BashlexShellParser(ShellParser):

    def parse(self, val: str) -> List[ShellObject]:
        nodes = bashlex.parse(val)
        res = []
        for node in nodes:
            res.extend(BashlexNodeTransformer.transform_node(node, val))
        return res
