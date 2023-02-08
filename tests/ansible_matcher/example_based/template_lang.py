import unittest
import string

from src.ansible_matcher.template_lang import *


class TestTemplateConstructor(unittest.TestCase):

    def setUp(self) -> None:
        self.templ_constr = TemplateConstructor()

    def test_template_word(self):
        words = [
            "Thequickbrownfoxjumpsoverthelazydog",
            "`1234567890-=~!@#$%^&*()_+[];'\\,./{}:\"|<>?",
            "{}}{}}}{}}}}" # might add more complex test in the future
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
        non_words = [
            "{{}}",
            "{{ }}",
            "{{\t}}",
        ] + [
            "{{f" + c + "l}}" for c in "\t `-=~!@#$%^&*()+[];'\\,./{}:\"|<>?"
        ] + [
            "{{f:om}}", "{{f:pm}}", "{{f:po}}"
        ]
        for n in non_words:
            t = self.templ_constr.from_str(n)
            assert t is None

        words = [
            "{{ " + c + " }}" for c in string.ascii_letters + "_"
        ] + [
            "{{ f" + c + " }}" for c in string.ascii_letters + string.digits + "_"
        ] + [
            "{{ name : " + c + " }}"
            for c in ["", "m", "o", "p"] + list(map(lambda x: "".join(x), itertools.combinations("mop", 2))) + ["mop"]
        ]
        templates = [self.templ_constr.from_str(w) for w in words]

        assert_values = [
            {"name": c, "pos": (0, 5), "spec_many": False, "spec_optional": False, "spec_path": False}
            for c in string.ascii_letters + "_"
        ] + [
            {"name": "f" + c, "pos": (0, 6), "spec_many": False, "spec_optional": False, "spec_path": False}
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
            for k, v in av.items():
                assert getattr(field, k) == v

    def test_template_part(self):
        pass

    def test_command_template(self):
        pass
