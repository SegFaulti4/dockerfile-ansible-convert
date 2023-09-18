from typing import List, Tuple, Optional
from dataclasses import dataclass

from src.exception import ShellParserException


class ShellObject:
    pass


class ShellScriptPart:
    pass


class ShellExpressionPart:
    pass


@dataclass
class ShellScript(ShellObject):
    line: str
    parts: List[ShellScriptPart]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellScriptPart) for part in parts)


@dataclass
class ShellExpression(ShellObject):
    line: str
    parts: List[ShellExpressionPart]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellExpressionPart) for part in parts) and \
               all(
                   all(isinstance(comm_part, ShellWordObject) for comm_part in part.parts)
                   for part in filter(lambda x: isinstance(x, ShellCommand), parts)
               )


@dataclass
class ShellRaw(ShellObject, ShellExpressionPart, ShellScriptPart):
    value: str


@dataclass
class ShellAssignment(ShellObject, ShellScriptPart):
    name: str
    descriptor: Optional[int]
    value: ShellExpression


class ShellOperator(ShellObject, ShellScriptPart):
    pass


@dataclass
class ShellOperatorOr(ShellOperator):
    pass


@dataclass
class ShellOperatorAnd(ShellOperator):
    pass


@dataclass
class ShellOperatorEnd(ShellOperator):
    pass


@dataclass
class ShellParameter(ShellObject):
    name: str
    pos: Tuple[int, int]


@dataclass
class ShellWordObject(ShellObject):
    value: str
    parts: List[ShellParameter]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellParameter) for part in parts)


# the only types of redirects encountered in dataset so far:
# 1) >      3) >>
# 2) <      4) >&
@dataclass
class ShellRedirect(ShellObject):
    rtype: str
    descriptor: Optional[int]
    word: ShellWordObject


@dataclass
class ShellCommand(ShellObject, ShellScriptPart, ShellExpressionPart):
    line: str
    words: List[ShellWordObject]
    redirects: List[ShellRedirect]


# class ShellPipelineObject(ShellObject):
#    pass


class ShellParser:

    def parse(self, val: str) -> List[ShellObject]:
        raise NotImplementedError

    @staticmethod
    def allowed_script_parts(parts: List[ShellObject]) -> bool:
        return ShellScript.allowed_parts(parts)

    @staticmethod
    def allowed_expression_parts(parts: List[ShellObject]) -> bool:
        return ShellExpression.allowed_parts(parts)

    def parse_as_script(self, line: str) -> ShellScript:

        def custom_strip(s: str, c: str) -> str:
            if s.startswith(c) and s.endswith(c):
                return s.strip(c)
            return s

        line = custom_strip(line, '"')
        line = custom_strip(line, "'")
        line = custom_strip(line, '"')
        parts = self.parse(line)
        if self.allowed_script_parts(parts):
            return ShellScript(parts=parts, line=line)
        raise ShellParserException("Found unallowed script parts")

    def parse_as_expression(self, line: str) -> ShellExpression:
        if not line:
            return ShellExpression(parts=[], line="")

        unquoted_flag = not line.startswith('"') or not line.endswith('"')

        # dirty workaround to skip some unwanted node types
        if unquoted_flag:
            line = '"' + line + '"'
        parts = self.parse(line)
        if self.allowed_expression_parts(parts):
            if unquoted_flag:
                line = line[1:-1]
                parts = self._unquote_parts(parts)
            return ShellExpression(parts=parts, line=line)
        raise ShellParserException("Found unallowed expression parts")

    @staticmethod
    def _unquote_parts(parts: List[ShellExpressionPart]) -> List[ShellExpressionPart]:
        last_part = parts[-1]
        if isinstance(last_part, ShellCommand):
            last_word = last_part.words[-1]
            if last_word.value.endswith('"'):
                last_word.value = last_word.value[:-1]
        elif isinstance(last_part, ShellRaw):
            if last_part.value.endswith('"'):
                last_part.value = last_part.value[:-1]

        first_part = parts[0]
        if isinstance(first_part, ShellCommand):
            first_word = first_part.words[0]
            if first_word.value.startswith('"'):
                first_word.value = first_word.value[1:]
                for part in first_word.parts:
                    part.pos = part.pos[0] - 1, part.pos[1] - 1
        elif isinstance(first_part, ShellRaw):
            if first_part.value.startswith('"'):
                first_part.value = first_part.value[1:]

        return parts
