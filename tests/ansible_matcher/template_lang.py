import unittest
import string
import logging

from src.ansible_matcher.template_lang import *
from src.log import globalLog


class TestTemplateConstructor(unittest.TestCase):

    RB = "<<"
    LB = ">>"

    def setUp(self):
        globalLog.setLevel(logging.INFO)
        self.templ_constr = TemplateConstructor()

    def test_template_word(self):
        rb = self.RB
        lb = self.LB
        words = [
            "Thequickbrownfoxjumpsoverthelazydog",
            "`1234567890-=~!@#$%^&*()_+[];'\\,./{}:\"|<>?",
            f"{rb[0]}{lb}{rb[0]}{lb}{lb[0]}{rb[0]}{lb}{lb}"  # might add more complex test in the future
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
        rb = self.RB
        lb = self.LB
        non_fields = [
            f"{rb}{lb}",
            f"{rb} {lb}",
            f"{rb}\t{lb}",
        ] + [
            f"{rb}r{c}l{lb}" for c in "\t `-=~!@#$%^&*()+[];'\\,./{}:\"|<>?"
        ] + [
            f"{rb}r:om{lb}", f"{rb}r:pm{lb}", f"{rb}r:po{lb}"
        ]
        for n in non_fields:
            t = self.templ_constr.from_str(n)
            assert t is None

        fields = [
            f"{rb}{c}{lb}" for c in string.ascii_letters + "_"
        ] + [
            f"{rb}r{c}{lb}" for c in string.ascii_letters + string.digits + "_"
        ] + [
            f"{rb}name : {c}{lb}"
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
                globalLog.info(k, v)
                assert getattr(field, k) == v
            globalLog.info()

    def test_template_part(self):
        rb = self.RB
        lb = self.LB
        non_parts = [
            f"{rb}name{lb}{rb}eman{lb}",
            f"something{rb} {lb}nothing"
        ]
        for n in non_parts:
            t = self.templ_constr.from_str(n)
            globalLog.info(t)
            assert t is None

        parts = [
            f"{rb}name{lb}",
            f"prefix{rb}name{lb}",
            f"{rb}name{lb}postfix",
            f"prefix{rb}name{lb}postfix",
            f"p1{rb}n1{lb}p2{rb}n2{lb}p3"
        ]
        templates = [self.templ_constr.from_str(p) for p in parts]

        assert_fields_repr = [
            [f"{rb}name{lb}"],
            [f"{rb}name{lb}"],
            [f"{rb}name{lb}"],
            [f"{rb}name{lb}"],
            [f"{rb}n1{lb}", f"{rb}n2{lb}"]
        ]
        assert_values = [
            {"value": parts[0], "parts": [{"name": "name", "pos": (0, len(f"{rb}name{lb}"))}]},
            {"value": parts[1], "parts": [{"name": "name", "pos": (len("prefix"), len(f"prefix{rb}name{lb}"))}]},
            {"value": parts[2], "parts": [{"name": "name", "pos": (0, len(f"{rb}name{lb}"))}]},
            {"value": parts[3], "parts": [{"name": "name", "pos": (len("prefix"), len(f"prefix{rb}name{lb}"))}]},
            {"value": parts[4], "parts": [
                {"name": "n1", "pos": (len("p1"), len(f"p1{rb}n1{lb}"))},
                {"name": "n2", "pos": (len(f"p1{rb}n1{lb}p2"), len(f"p1{rb}n1{lb}p2{rb}n2{lb}"))}
            ]},
        ]
        for t, av, afr in zip(templates, assert_values, assert_fields_repr):
            assert isinstance(t, list)
            assert len(t) == 1
            assert isinstance(t[0], TemplatePart)

            part: TemplatePart = t[0]
            globalLog.info(part)
            globalLog.info()
            assert part.value == av["value"]
            for f, af, ar in zip(part.parts, av["parts"], afr):
                globalLog.info(f, af, ar)
                assert f.name == af["name"]
                assert f.pos == af["pos"]
                assert part.value[f.pos[0]:f.pos[1]] == ar
            globalLog.info()

    def test_command_template(self):
        rb = self.RB
        lb = self.LB
        non_templates = [
            f"{rb}name{lb}  {rb}name{lb}{rb}eman{lb}",
            f"everything something{rb} {lb}nothing"
        ]
        for n in non_templates:
            t = self.templ_constr.from_str(n)
            globalLog.info(t)
            assert t is None


class TestTemplateTweaks(unittest.TestCase):
    pass


class TestCommandTemplateMatcher(unittest.TestCase):
    pass


class TestTemplateFiller(unittest.TestCase):
    RB = "<<"
    LB = ">>"

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
