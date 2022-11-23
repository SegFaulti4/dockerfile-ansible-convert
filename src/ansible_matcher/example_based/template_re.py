from template_lang import *


if __name__ == "__main__":
    from sandbox.shell_parser.main import SandboxShellParser

    shell_parser = SandboxShellParser()

    re_str = fr"{CommandTemplateMatcher._RE_SHELL_WORD_SEP}".join([
        r"^mkdir",
        r"--context=(?P<field_system>.*):(?P<field_object>.*):(?P<field_content>.*)",
        r"(?P<param>.*)$"
    ])

    matching_str = "mkdir --context=sys_$SYS:obj_$OBJ:cont_$CONT $DIR"
    matching_parsed = shell_parser.parse(matching_str)

    matching_prepped = CommandTemplateMatcher._preprocess_command(matching_parsed[0].parts)[0]

    print(re_str)
    print(matching_prepped)
    match = re.fullmatch(re_str, matching_prepped)

    for key, value in match.groupdict().items():
        if value is not None:
            start, end = match.span(key)
            print(start, end, key, value)
