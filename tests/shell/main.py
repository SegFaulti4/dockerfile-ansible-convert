import unittest

from src.shell.main import *
from src.shell.bashlex.main import *


class TestShellParser(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = BashlexShellParser()

    def test_parameter(self):
        words = [
            "$PAR_1//",
            "/$PAR_2/",
            "//$PAR_3"
        ]
        parsed_words = [self.parser.parse(word) for word in words]

        # av - assert values
        assert_values = [
            [ShellParameterObject(name="PAR_1", pos=(0, 6))],
            [ShellParameterObject(name="PAR_2", pos=(1, 7))],
            [ShellParameterObject(name="PAR_3", pos=(2, 8))]
        ]
        for parsed, word_params_av in zip(parsed_words, assert_values):
            assert isinstance(parsed, list) and len(parsed) == 1
            assert isinstance(parsed[0], ShellCommandObject) and len(parsed[0].parts) == 1

            word = parsed[0].parts[0]
            assert isinstance(word, ShellWordObject)
            assert len(word.parts) == len(word_params_av)
            for param, param_av in zip(word.parts, word_params_av):
                assert param == param_av

    def test_word(self):
        words = [
            "$PAR_1/$PAR_2/",
            "/$PAR_3/$PAR_4",
            "$PAR_5//$PAR_6",
            "$PAR_7/$PAR_8/$PAR_9",
            "no-parameters-here"
        ]
        parsed_words = [self.parser.parse(word) for word in words]

        assert_values = [
            ShellWordObject(value=words[0], parts=[
                ShellParameterObject(name="PAR_1", pos=(0, 6)),
                ShellParameterObject(name="PAR_2", pos=(7, 13))
            ]),
            ShellWordObject(value=words[1], parts=[
                ShellParameterObject(name="PAR_3", pos=(1, 7)),
                ShellParameterObject(name="PAR_4", pos=(8, 14))
            ]),
            ShellWordObject(value=words[2], parts=[
                ShellParameterObject(name="PAR_5", pos=(0, 6)),
                ShellParameterObject(name="PAR_6", pos=(8, 14))
            ]),
            ShellWordObject(value=words[3], parts=[
                ShellParameterObject(name="PAR_7", pos=(0, 6)),
                ShellParameterObject(name="PAR_8", pos=(7, 13)),
                ShellParameterObject(name="PAR_9", pos=(14, 20))
            ]),
            ShellWordObject(value=words[4], parts=[])
        ]
        for parsed, word_av in zip(parsed_words, assert_values):
            assert isinstance(parsed, list) and len(parsed) == 1
            assert isinstance(parsed[0], ShellCommandObject) and len(parsed[0].parts) == 1

            word = parsed[0].parts[0]
            assert word == word_av

    def test_operator(self):
        comm = "w && w || w || w && w;"
        parsed = self.parser.parse(comm)

        # av - assert values
        assert_values = [
            ShellOperatorAndObject(),
            ShellOperatorOrObject(),
            ShellOperatorOrObject(),
            ShellOperatorAndObject(),
            ShellOperatorEndObject()
        ]
        assert isinstance(parsed, list) and len(parsed) == 10

        operators = parsed[1::2]
        assert operators == assert_values

    def test_assignment(self):
        assigns = [
            "name=value1",
            "name=$(value2)"
        ]
        parsed_assigns = [self.parser.parse(assign) for assign in assigns]

        assert_values = ["name", "name"]
        for parsed, name_av in zip(parsed_assigns, assert_values):
            print(parsed)

            assert isinstance(parsed, list) and len(parsed) == 1
            assert isinstance(parsed[0], ShellAssignmentObject)
            assert parsed[0].name == name_av
            assert isinstance(parsed[0].value, ShellExpression)

    def test_command(self):
        commands = [
            "word1 word2 word3",
            "word4/$PAR1 $PAR2/word5 wo/$PAR3/rd6"
        ]
        parsed_commands = [self.parser.parse(comm) for comm in commands]

        assert_types = [
            [ShellWordObject, ShellWordObject, ShellWordObject],
            [ShellWordObject, ShellWordObject, ShellWordObject]
        ]
        for parsed, command, part_types in zip(parsed_commands, commands, assert_types):
            assert isinstance(parsed, list) and len(parsed) == 1
            assert isinstance(parsed[0], ShellCommandObject)

            assert parsed[0].line == command
            parts = parsed[0].parts
            assert len(parts) == len(part_types)
            assert all(isinstance(part, part_type) for part, part_type in zip(parts, part_types))

    def test_raw(self):
        commands = [
            "redirects > are yet < to be supported",
            '"$(command)" substitutions are yet to be supported'
        ]
        parsed_commands = [self.parser.parse(comm) for comm in commands]

        for parsed, command in zip(parsed_commands, commands):
            assert isinstance(parsed, list) and len(parsed) == 1
            assert isinstance(parsed[0], ShellRawObject)
            assert parsed[0].value == command

    def test_shell_script(self):
        scripts = [
            'regular command && raw object because of "$(substitution)"',
            "logical || sequence && of && commands || ending || with && operator end;",
            "assignment=before && regular command"
        ]
        parsed_scripts = [self.parser.parse_as_script(script) for script in scripts]

        comm, raw, assign = ShellCommandObject, ShellRawObject, ShellAssignmentObject
        a, o, e = ShellOperatorAndObject, ShellOperatorOrObject, ShellOperatorEndObject
        assert_types = [
            [comm, a, raw],
            [comm, o, comm, a, comm, a, comm, o, comm, o, comm, a, comm, e],
            [assign, a, comm]
        ]
        for parsed, part_types, script in zip(parsed_scripts, assert_types, scripts):
            assert isinstance(parsed, ShellScript)
            assert parsed.line == script
            assert len(parsed.parts) == len(part_types)
            assert all(isinstance(part, part_type) for part, part_type in zip(parsed.parts, part_types))

    def test_shell_expression(self):
        expressions = [
            "'wget gcc gcc-multilib libc6-dev-i386 make'",
            '"$(mktemp -d)"',
            "$RABBITMQ_HOME/sbin/rabbitmq-defaults"
        ]
        parsed_expr = [self.parser.parse_as_expression(expr) for expr in expressions]

        assert all(isinstance(parsed, ShellExpression) for parsed in parsed_expr)
        assert len(parsed_expr[0].parts) == 1 and isinstance(parsed_expr[0].parts[0], ShellCommandObject)
        assert len(parsed_expr[1].parts) == 1 and isinstance(parsed_expr[1].parts[0], ShellRawObject)
        assert len(parsed_expr[2].parts) == 1 and isinstance(parsed_expr[2].parts[0], ShellCommandObject)
