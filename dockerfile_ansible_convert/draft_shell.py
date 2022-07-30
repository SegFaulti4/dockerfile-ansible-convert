from typing import List, Tuple
from dataclasses import dataclass

from draft_exception import ShellParserException


class ShellScriptPart:
    pass


@dataclass
class ShellScript:
    parts: List[ShellScriptPart]


class ShellExpressionPart:
    pass


@dataclass
class ShellExpression:
    parts: List[ShellExpressionPart]


class ShellObject:
    pass


class ShellParser:

    def parse(self, val: str) -> List[ShellObject]:
        raise NotImplementedError

    @staticmethod
    def allowed_script_parts(parts: List[ShellObject]) -> bool:
        return all(isinstance(part, ShellScriptPart) for part in parts)

    @staticmethod
    def allowed_expression_parts(parts: List[ShellObject]) -> bool:
        return all(isinstance(part, ShellExpressionPart) for part in parts)

    def parse_as_script(self, val: str) -> ShellScript:
        parts = self.parse(val)
        if self.allowed_script_parts(parts):
            return ShellScript(parts=parts)
        raise ShellParserException("Found unallowed script parts")

    def parse_as_expression(self, val: str) -> ShellExpression:
        parts = self.parse(val)
        if self.allowed_expression_parts(parts):
            return ShellExpression(parts=parts)
        raise ShellParserException("Found unallowed expression parts")


@dataclass
class ShellRawObject(ShellObject, ShellExpressionPart, ShellScriptPart):
    value: str


class ShellCommandPart:
    pass


@dataclass
class ShellCommandObject(ShellObject, ShellScriptPart):
    parts: List[ShellCommandPart]
    line: str


class ShellAssignmentPart:
    pass


@dataclass
class ShellAssignmentObject(ShellObject, ShellScriptPart):
    name: str
    value: ShellAssignmentPart


class ShellOperatorObject(ShellObject, ShellScriptPart):
    pass


class ShellOperatorOrObject(ShellOperatorObject):
    pass


class ShellOperatorAndObject(ShellOperatorObject):
    pass


class ShellOperatorEndObject(ShellOperatorObject):
    pass


class ShellWordPart:
    pass


@dataclass
class ShellWordObject(ShellObject, ShellAssignmentPart, ShellCommandPart):
    value: str
    parts: List[ShellWordPart]


@dataclass
class ShellParameterObject(ShellObject, ShellWordPart):
    name: str
    pos: Tuple[int, int]


# class ShellRedirectObject(ShellObject):
#    pass


# class ShellPipelineObject(ShellObject):
#    pass
