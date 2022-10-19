class ConvertException(Exception):
    pass


class ShellParserException(ConvertException):
    pass


class BashlexShellParserException(ShellParserException):
    pass


class DockerfileGeneratorException(ConvertException):
    pass


class TPDockerfileGeneratorException(DockerfileGeneratorException):
    pass


class RoleGeneratorException(ConvertException):
    pass
