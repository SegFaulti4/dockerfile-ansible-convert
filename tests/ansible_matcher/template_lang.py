import unittest
import string

from src.ansible_matcher.template_lang import *


class TestTemplateConstructor(unittest.TestCase):

    RB = "<<"
    LB = ">>"

    def setUp(self) -> None:
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
            print(field)
            for k, v in av.items():
                print(k, v)
                assert getattr(field, k) == v

    def test_template_part(self):
        rb = self.RB
        lb = self.LB
        non_parts = [
            f"{rb}name{lb}{rb}eman{lb}",
            f"something{rb} {lb}nothing"
        ]
        for n in non_parts:
            t = self.templ_constr.from_str(n)
            assert t is None


    def test_command_template(self):
        pass
