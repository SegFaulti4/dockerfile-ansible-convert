import unittest
import string
import logging

from src.shell.bashlex.main import BashlexShellParser

from src.ansible_matcher.template_lang import *
from src.log import globalLog


LB = "<<"
RB = ">>"


class TestTemplateConstructor(unittest.TestCase):

    def setUp(self):
        globalLog.setLevel(logging.INFO)
        self.templ_constr = TemplateConstructor()

    def test_template_word(self):
        words = [
            "Thequickbrownfoxjumpsoverthelazydog",
            "`1234567890-=~!@#$%^&*()_+[];'\\,./{}:\"|<>?",
            f"{LB[0]}{RB}{LB[0]}{RB}{RB[0]}{LB[0]}{RB}{RB}"  # might add more complex test in the future
            # see https://github.com/SegFaulti4/dockerfile-ansible-convert/issues/17
        ]

        templates = [self.templ_constr.from_str(w) for w in words]
        for t, w in zip(templates, words):
            assert isinstance(t, list)
            assert len(t) == 1
            assert isinstance(t[0], TemplatePart)
            assert not t[0].parts
            assert t[0].value == w

    def test_template_field(self):
        non_fields = [
            f"{LB}{RB}",
            f"{LB} {RB}",
            f"{LB}\t{RB}",
        ] + [
            f"{LB}r{c}l{RB}" for c in "\t `-=~!@#$%^&*()+[];'\\,./{}:\"|<>?"
        ] + [
            f"{LB}r:om{RB}", f"{LB}r:pm{RB}", f"{LB}r:po{RB}"
        ]
        for n in non_fields:
            t = self.templ_constr.from_str(n)
            assert t is None

        fields = [
            f"{LB}{c}{RB}" for c in string.ascii_letters + "_"
        ] + [
            f"{LB}r{c}{RB}" for c in string.ascii_letters + string.digits + "_"
        ] + [
            f"{LB}name : {c}{RB}"
            for c in ["", "m", "o", "p"] + list(map(lambda x: "".join(x), itertools.combinations("mop", 2))) + ["mop"]
        ]
        templates = [self.templ_constr.from_str(w) for w in fields]

        assert_values = [
            {"name": c, "pos": (0, 5), "spec_many": False, "spec_optional": False, "spec_path": False}
            for c in string.ascii_letters + "_"
        ] + [
            {"name": "r" + c, "pos": (0, 6), "spec_many": False, "spec_optional": False, "spec_path": False}
            for c in string.ascii_letters + string.digits + "_"
        ] + [
            {"name": "name", "pos": (0, 9 + len(c)),
             "spec_many": c.count("m") == 1, "spec_optional": c.count("o") == 1, "spec_path": c.count("p") == 1}
            for c in ["", "m", "o", "p"] + list(map(lambda x: "".join(x), itertools.combinations("mop", 2))) + ["mop"]
        ]
        for t, av in zip(templates, assert_values):
            assert isinstance(t, list)
            assert len(t) == 1
            assert isinstance(t[0], TemplatePart)
            assert len(t[0].parts) == 1

            field = t[0].parts[0]
            globalLog.info(field)
            for k, v in av.items():
                globalLog.info("%s %s", k, v)
                assert getattr(field, k) == v
            globalLog.info("")

    def test_template_part(self):
        non_parts = [
            f"{LB}name{RB}{LB}eman{RB}",
            f"something{LB} {RB}nothing"
        ]
        for n in non_parts:
            t = self.templ_constr.from_str(n)
            globalLog.info(t)
            assert t is None

        parts = [
            f"{LB}name{RB}",
            f"prefix{LB}name{RB}",
            f"{LB}name{RB}postfix",
            f"prefix{LB}name{RB}postfix",
            f"p1{LB}n1{RB}p2{LB}n2{RB}p3"
        ]
        templates = [self.templ_constr.from_str(p) for p in parts]

        assert_fields_repr = [
            [f"{LB}name{RB}"],
            [f"{LB}name{RB}"],
            [f"{LB}name{RB}"],
            [f"{LB}name{RB}"],
            [f"{LB}n1{RB}", f"{LB}n2{RB}"]
        ]
        assert_values = [
            {"value": parts[0], "parts": [{"name": "name", "pos": (0, len(f"{LB}name{RB}"))}]},
            {"value": parts[1], "parts": [{"name": "name", "pos": (len("prefix"), len(f"prefix{LB}name{RB}"))}]},
            {"value": parts[2], "parts": [{"name": "name", "pos": (0, len(f"{LB}name{RB}"))}]},
            {"value": parts[3], "parts": [{"name": "name", "pos": (len("prefix"), len(f"prefix{LB}name{RB}"))}]},
            {"value": parts[4], "parts": [
                {"name": "n1", "pos": (len("p1"), len(f"p1{LB}n1{RB}"))},
                {"name": "n2", "pos": (len(f"p1{LB}n1{RB}p2"), len(f"p1{LB}n1{RB}p2{LB}n2{RB}"))}
            ]},
        ]
        for t, av, afr in zip(templates, assert_values, assert_fields_repr):
            assert isinstance(t, list)
            assert len(t) == 1
            assert isinstance(t[0], TemplatePart)

            part: TemplatePart = t[0]
            globalLog.info(part)
            globalLog.info("")
            assert part.value == av["value"]
            for f, af, ar in zip(part.parts, av["parts"], afr):
                globalLog.info("%s %s %s", f, af, ar)
                assert f.name == af["name"]
                assert f.pos == af["pos"]
                assert part.value[f.pos[0]:f.pos[1]] == ar
            globalLog.info("")

    def test_command_template(self):
        non_templates = [
            f"{LB}name{RB}  {LB}name{RB}{LB}eman{RB}",
            f"everything something{LB} {RB}nothing"
            # TODO: check that all duplicate fields have same options
        ]
        for n in non_templates:
            t = self.templ_constr.from_str(n)
            globalLog.info(t)
            assert t is None

        templates_str = [
            "a "  # this one tests template postfix
        ]
        templates = [self.templ_constr.from_str(t) for t in templates_str]

        assert_values = [
            [{"value": "a", "parts": []}, {"value": "", "parts": []}]
        ]
        for t, av, in zip(templates, assert_values):
            assert isinstance(t, list)
            assert len(t) == len(av)
            assert all(isinstance(p, TemplatePart) for p in t)

            for p, pav in zip(t, av):
                assert p.value == pav["value"]
                assert len(p.parts) == len(pav["parts"])
                assert all(isinstance(f, TemplateField) for f in p.parts)


class TestTemplateTweaks(unittest.TestCase):
    pass


class TestCommandTemplateMatcher(unittest.TestCase):

    """
    что хотелось бы отловить в этих тестах:
    2) матчинг строк с простыми полями
    3) матчинг полей с флагами
    4) неполное совпадение
    5) мерджинг двух результатов

    """

    def setUp(self):
        globalLog.setLevel(logging.INFO)
        self.templ_constr = TemplateConstructor()
        self.shell_parser = BashlexShellParser()

    def _match_strings(self, templ_str: str, shell_str: str) -> Optional[TemplateMatchResult]:
        template = self.templ_constr.from_str(templ_str)
        matcher = CommandTemplateMatcher(template=template)

        words = self.shell_parser.parse_as_script(shell_str)
        words = words.parts[0].parts
        return matcher.full_match(words)

    def _partial_match_strings(self, templ_str: str, shell_str: str) -> Optional[Tuple[TemplateMatchResult, str]]:
        template = self.templ_constr.from_str(templ_str)
        matcher = CommandTemplateMatcher(template=template)

        words = self.shell_parser.parse_as_script(shell_str)
        words = words.parts[0].parts
        res = matcher.match(words)
        if res is None:
            return res
        return res[0], " ".join(w.value for w in res[1])

    def _test_matching(self, matching: Dict, partial: bool = False):
        for i, items in enumerate(matching.items()):
            s, assert_res = items
            templ_str, shell_str = s
            if partial:
                match = self._partial_match_strings(templ_str, shell_str)
            else:
                match = self._match_strings(templ_str, shell_str)

            if match is None or match != assert_res:
                globalLog.warning(f"Failed to match on example {i}")
                assert False

    def _test_non_matching(self, non_matching: List):
        for templ_str, shell_str in non_matching:
            match = self._match_strings(templ_str, shell_str)
            assert match is None

    def test_basic_fields(self):
        matching = {
            # EXAMPLES:
            # 0) two identical non-parameterized words should match
            ("abcd", "abcd"):
                {},
            # 1) two identical sets of space separated non-parameterized words should match
            ("a bb ccc dddd", "a bb ccc dddd"):
                {},
            # 2) field-only template part should match any non-parameterized word
            (f"{LB}field{RB}", "var"):
                {"field": "var"},
            # 3) if non-parameterized word has same prefix and postfix as single-field template part
            #    they should match...
            (f"{LB}field1{RB} pre{LB}field2{RB} {LB}field3{RB}post", "pre_var1_post pre_var2_post pre_var3_post"):
                {"field1": "pre_var1_post", "field2": "_var2_post", "field3": "pre_var3_"},
            # 4) ...even if field value would be empty
            (f"pre{LB}field{RB}post", "prepost"):
                {"field": ""},
            # 5) fields should absorb the longest possible string inside non-parameterized word
            (f"{LB}field1{RB} pre{LB}field2{RB}mid{LB}field3{RB}post", "pre_var1_post pre_var2_mid_var3_mid_var4_post"):
                {"field1": "pre_var1_post", "field2": "_var2_mid_var3_", "field3": "_var4_"},
            # 6) fields should absorb single vars...
            (f"{LB}field{RB}", "$VAR"):
                {"field": "$VAR"},
            # 7) ...as well as multiple vars
            (f"pre{LB}field{RB}post", "prePRE${VAR1}MID${VAR2}POSTpost"):
                {"field": "PRE${VAR1}MID${VAR2}POST"},
            # 8) example 3 remains true for parameterized words
            (f"{LB}field1{RB} pre{LB}field2{RB} {LB}field3{RB}post", "pre${VAR1}post pre${VAR2}post pre${VAR3}post"):
                {"field1": "pre${VAR1}post", "field2": "${VAR2}post", "field3": "pre${VAR3}"},
            # 9) example 5 remains true for parameterized words
            (f"pre{LB}field1{RB}mid{LB}field2{RB}post", "pre_PRE${VAR1}POST_mid_${VAR2}_mid_PRE${VAR3}POST_post"):
                {"field1": "_PRE${VAR1}POST_mid_${VAR2}_", "field2": "_PRE${VAR3}POST_"},
            # 10) fields can't absorb space characters
            (f"pre{LB}field1{RB} mid{LB}field2{RB}post", "pre_PRE${VAR1}POST mid_${VAR2}_mid_PRE${VAR3}POST_post"):
                {"field1": "_PRE${VAR1}POST", "field2": "_${VAR2}_mid_PRE${VAR3}POST_"},

            # 11) if same field is used multiple times - only the last value will be used
            (f"{LB}field{RB} {LB}field{RB}", "word1 word2"):
                {"field": "word2"}
        }
        non_matching = [
            ("a", "b"),
            ("a bb ccc dddd", "a bbb ccc dddd"),
            # fields can't absorb space characters
            (f"{LB}field{RB}", "a b"),
            # only fields can absorb vars
            (f"{LB}field1{RB}${{VAR1}}{LB}field2{RB}", "pre${VAR1}post")
        ]
        self._test_matching(matching)
        self._test_non_matching(non_matching)

    def test_field_options(self):
        matching = {
            # EXAMPLES FOR 'many' OPTION:
            # 0) 'many' field can absorb multiple words
            (f"{LB}field:m{RB}", "var1 var2 var3"):
                {"field": ["var1", "var2", "var3"]},
            # 1) 'many' field absorbs only matching words
            (f"pre {LB}field:m{RB} post", "pre var1 var2 var3 post"):
                {"field": ["var1", "var2", "var3"]},
            # 2) 'many' field absorbs words greedily...
            (f"{LB}field1:m{RB} var2 {LB}field2:m{RB}", "var1 var2 var2 var3"):
                {"field1": ["var1", "var2"], "field2": ["var3"]},
            # 3) 'many' field affects its whole parent template part
            # but doesn't affect 'non-many' fields from same template part
            (f"pre{LB}field1:m{RB}mid{LB}field2{RB}post", "pre1mid1post pre2mid2post pre3mid3post"):
                {"field1": ["1", "2", "3"], "field2": "3"},

            # EXAMPLES FOR 'optional' OPTION:
            # 4) 'optional' field makes its parent template part optional
            # (it can be missing from matching command)
            (f"pre {LB}field:o{RB} post", "pre post"):
                {},
            # 5) other fields from the same template part need to have 'optional' option
            # to be matched when the word is missing
            (f"pre {LB}field1:o{RB}mid{LB}field2:o{RB}", "pre"):
                {},
            # 6) if optional word is not missing from matching command
            # everything works as normal
            (f"pre {LB}field1:o{RB}mid{LB}field2{RB}", "pre 1mid2"):
                {"field1": "1", "field2": "2"},
            # 7) 'optional' fields can be paired with 'many' fields
            # or even have 'many' option themselves
            # the rule from example 5 is still true though
            (f"pre {LB}field1:mo{RB}mid{LB}field2:mo{RB}", "pre"):
                {},
            # 8) ...if optional word is not missing from matching command
            # everything works as normal
            (f"pre {LB}field1:o{RB}mid{LB}field2:m{RB}", "pre 1mid1 2mid2 3mid3"):
                {"field1": "3", "field2": ["1", "2", "3"]},

            # EXAMPLES FOR 'path' OPTION:
            # 9) 'path' option doesn't affect matching process
            (f"{LB}field1:p{RB} pre{LB}field2:p{RB} {LB}field3:p{RB}post",
             "pre${VAR1}post pre${VAR2}post pre${VAR3}post"):
                {"field1": "pre${VAR1}post", "field2": "${VAR2}post", "field3": "pre${VAR3}"},
            # 10) 'path' option doesn't affect matching process
            (f"pre{LB}field1:p{RB}mid{LB}field2:p{RB}post",
             "pre_PRE${VAR1}POST_mid_${VAR2}_mid_PRE${VAR3}POST_post"):
                {"field1": "_PRE${VAR1}POST_mid_${VAR2}_", "field2": "_PRE${VAR3}POST_"},
            # 11) 'path' option doesn't affect matching process
            (f"pre{LB}field1:p{RB} mid{LB}field2:p{RB}post",
             "pre_PRE${VAR1}POST mid_${VAR2}_mid_PRE${VAR3}POST_post"):
                {"field1": "_PRE${VAR1}POST", "field2": "_${VAR2}_mid_PRE${VAR3}POST_"},
        }
        self._test_matching(matching)

    def test_non_full_match(self):
        matching = {
            ("var1", "var1 var2"):
                ({}, "var2"),
            (f"{LB}field1{RB}1", "var1 var2"):
                ({"field1": "var"}, "var2"),
            (f"{LB}field1:m{RB}1 {LB}field2{RB}1", "var1 var1 var1 var2 var3"):
                ({"field1": ["var", "var"], "field2": "var"}, "var2 var3")
        }
        self._test_matching(matching, partial=True)

    def test_results_merging(self):
        pass


class TestTemplateFiller(unittest.TestCase):
    LB = "<<"
    RB = ">>"

    def setUp(self):
        globalLog.setLevel(logging.INFO)
        rb = self.RB
        lb = self.LB
        self.templ_constr = TemplateConstructor()
        self.templ_strings = [
            f"{rb}single{lb}",
            f"{rb}many{lb}",
            f"{rb}optional{lb}",
            f"word {rb}single{lb} word {rb}many{lb} word {rb}optional{lb} word"
        ]
        self.fields_dict = {
            "single": "single",
            "many": ["1", "2", "3"]
        }
        self.templates = [self.templ_constr.from_str(s) for s in self.templ_strings]
        assert all(t is not None for t in self.templates)

    def test_fill_flatten(self):
        flatten_non_strict = [TemplateFiller(t).fill_flatten(self.fields_dict, strict=False) for t in self.templates]
        flatten_strict = [TemplateFiller(t).fill_flatten(self.fields_dict, strict=True) for t in self.templates]

        globalLog.info(flatten_non_strict)
        globalLog.info(flatten_strict)

        assert flatten_non_strict == [
            "single", "1 2 3", "", "word single word 1 2 3 word  word"
        ]
        assert flatten_strict == [
            "single", "1 2 3", None, None
        ]

    def test_fill_expand(self):
        expand_non_strict = [TemplateFiller(t).fill_expand(self.fields_dict, strict=False) for t in self.templates]
        expand_strict = [TemplateFiller(t).fill_expand(self.fields_dict, strict=True) for t in self.templates]

        globalLog.info(expand_non_strict)
        globalLog.info(expand_strict)

        assert expand_non_strict == [
            ["single"], ["1", "2", "3"], [""],
            ['word single word 1 word  word', 'word single word 2 word  word', 'word single word 3 word  word']
        ]
        assert expand_strict == [
            ['single'], ['1', '2', '3'], None, None
        ]
