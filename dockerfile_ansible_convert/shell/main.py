from typing import List, Tuple
from dataclasses import dataclass

from draft_exception import ShellParserException


class ShellObject:
    pass


class ShellScriptPart:
    pass


class ShellExpressionPart:
    pass


class ShellAssignmentPart:
    pass


class ShellCommandPart:
    pass


class ShellWordPart:
    pass


@dataclass
class ShellScript(ShellObject):
    parts: List[ShellScriptPart]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellScriptPart) for part in parts)


@dataclass
class ShellExpression(ShellObject, ShellAssignmentPart):
    parts: List[ShellExpressionPart]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellExpressionPart) for part in parts)


@dataclass
class ShellRawObject(ShellObject, ShellExpressionPart, ShellScriptPart):
    value: str


@dataclass
class ShellCommandObject(ShellObject, ShellScriptPart):
    parts: List[ShellCommandPart]
    line: str

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellCommandPart) for part in parts)


@dataclass
class ShellAssignmentObject(ShellObject, ShellScriptPart):
    name: str
    value: ShellAssignmentPart

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellAssignmentPart) for part in parts)


class ShellOperatorObject(ShellObject, ShellScriptPart):
    pass


class ShellOperatorOrObject(ShellOperatorObject):
    pass


class ShellOperatorAndObject(ShellOperatorObject):
    pass


class ShellOperatorEndObject(ShellOperatorObject):
    pass


@dataclass
class ShellWordObject(ShellObject, ShellAssignmentPart, ShellCommandPart):
    value: str
    parts: List[ShellWordPart]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellWordPart) for part in parts)


@dataclass
class ShellParameterObject(ShellObject, ShellWordPart):
    name: str
    pos: Tuple[int, int]


# class ShellRedirectObject(ShellObject):
#    pass


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
