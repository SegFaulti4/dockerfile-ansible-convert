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
                child = [ShellRaw(value=line[part.pos[0]:part.pos[1]])]
            res.extend(child)
        return res

    @staticmethod
    def transform_command(node: bashlex.ast.node, line) \
            -> Union[List[ShellRaw], List[ShellAssignment], List[ShellCommand]]:

        comm_line = line[node.pos[0]:node.pos[1]]
        parts: List[ShellObject] = []

        # node classified in bashlex as "command" might be something different (e.g. "assignment")
        for part in node.parts:
            transformed = BashlexNodeTransformer.transform_node(part, line)
            if not transformed:
                return [ShellRaw(value=comm_line)]
            parts.extend(transformed)

        # check for assignment
        if len(parts) == 1 and isinstance(parts[0], ShellAssignment):
            # noinspection PyTypeChecker
            return [parts[0]]

        # currently not used
        # check for export assignment
        # if len(parts) == 2 and all(isinstance(p, WordNode) for p in parts) and parts[0].value == "export":
        #    second_part = parse_bash_commands(node.parts[1].word)
        #    if len(second_part) == 1 and isinstance(second_part[0], AssignmentNode):
        #        return second_part

        if not (parts and
                any(isinstance(part, ShellWordObject)
                    for part in parts) and
                all(isinstance(part, ShellWordObject) or isinstance(part, ShellRedirect)
                    for part in parts)):
            return [ShellRaw(value=comm_line)]

        # noinspection PyTypeChecker
        words: List[ShellWordObject] = list(filter(lambda x: isinstance(x, ShellWordObject), parts))
        # noinspection PyTypeChecker
        redirects: List[ShellRedirect] = list(filter(lambda x: isinstance(x, ShellRedirect), parts))

        return [ShellCommand(line=comm_line, words=words, redirects=redirects)]

    @staticmethod
    def transform_operator(node: bashlex.ast.node, line: str) -> List[ShellOperator]:
        if node.op == ';':
            return [ShellOperatorEnd()]
        elif node.op == '&&':
            return [ShellOperatorAnd()]
        elif node.op == '||':
            return [ShellOperatorOr()]

    @staticmethod
    def transform_assignment(node: bashlex.ast.node, line: str) -> List[ShellAssignment]:
        eq_pos = node.word.find('=')
        name, value = node.word[0:eq_pos], node.word[eq_pos + 1:]

        # workaround added to parse_as_expression
        # if not value.startswith('"') or not value.endswith('"'):
        #     value = '"' + value + '"'

        # Circular dependency
        part = BashlexShellParser().parse_as_expression(value)
        return [ShellAssignment(name=name, value=part)]

    @staticmethod
    def transform_commandsubstitution(node: bashlex.ast.node, line: str) -> List[ShellRaw]:
        return [ShellRaw(value=line[node.pos[0]:node.pos[1]])]

    @staticmethod
    def transform_parameter(node: bashlex.ast.node, line: str) -> List[ShellParameter]:
        return [ShellParameter(name=node.value, pos=(node.pos[0], node.pos[1]))]

    @staticmethod
    def transform_word(node, line) -> List[Union[ShellWordObject, ShellRaw]]:
        parts = []
        word_line = line[node.pos[0]:node.pos[1]]
        for part in node.parts:
            part.pos = part.pos[0] - node.pos[0], part.pos[1] - node.pos[0]
            parts.extend(BashlexNodeTransformer.transform_node(part, line))
        if ShellWordObject.allowed_parts(parts):
            return [ShellWordObject(value=word_line, parts=parts)]
        return [ShellRaw(value=word_line)]

    @staticmethod
    def transform_tilde(node, line):
        return []

    @staticmethod
    def transform_redirect(node: bashlex.ast.node, line: str) -> List[Union[ShellRedirect, ShellRaw]]:
        words = BashlexNodeTransformer.transform_node(node.output, line)
        if len(words) != 1 or not isinstance(words[0], ShellWordObject):
            return [ShellRaw(value=line[node.pos[0]:node.pos[1]])]

        # noinspection PyTypeChecker
        word: ShellWordObject = words[0]
        descriptor: Optional[int] = node.input
        rtype: str = node.type

        return [ShellRedirect(rtype=rtype, descriptor=descriptor, word=word)]


class BashlexShellParser(ShellParser):

    def parse(self, val: str) -> List[ShellObject]:
        nodes = bashlex.parse(val)
        res = []
        for node in nodes:
            transformed = BashlexNodeTransformer.transform_node(node, val)

            # transform_node can return empty list
            # in that case we create ShellRawObject
            if not transformed:
                res.append(ShellRaw(value=val[node.pos[0]:node.pos[1]]))
            else:
                res.extend(transformed)
        return res
