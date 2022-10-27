from typing import List, Tuple
from dataclasses import dataclass

from draft_exception import ShellParserException


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
                   for part in filter(lambda x: isinstance(x, ShellCommandObject), parts)
               )


@dataclass
class ShellRawObject(ShellObject, ShellExpressionPart, ShellScriptPart):
    value: str


@dataclass
class ShellAssignmentObject(ShellObject, ShellScriptPart):
    name: str
    value: ShellExpression


class ShellOperatorObject(ShellObject, ShellScriptPart):
    pass


@dataclass
class ShellOperatorOrObject(ShellOperatorObject):
    pass


@dataclass
class ShellOperatorAndObject(ShellOperatorObject):
    pass


@dataclass
class ShellOperatorEndObject(ShellOperatorObject):
    pass


@dataclass
class ShellParameterObject(ShellObject):
    name: str
    pos: Tuple[int, int]


@dataclass
class ShellWordObject(ShellObject):
    value: str
    parts: List[ShellParameterObject]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellParameterObject) for part in parts)


@dataclass
class ShellCommandObject(ShellObject, ShellScriptPart, ShellExpressionPart):
    line: str
    parts: List[ShellWordObject]

    @staticmethod
    def allowed_parts(parts: List[ShellObject]):
        return all(isinstance(part, ShellWordObject) for part in parts)


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

    def parse_as_script(self, line: str) -> ShellScript:
        parts = self.parse(line)
        if self.allowed_script_parts(parts):
            return ShellScript(parts=parts, line=line)
        raise ShellParserException("Found unallowed script parts")

    def parse_as_expression(self, line: str) -> ShellExpression:
        parts = self.parse(line)
        if self.allowed_expression_parts(parts):
            return ShellExpression(parts=parts, line=line)
        raise ShellParserException("Found unallowed expression parts")
