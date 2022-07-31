class ConvertException(Exception):
    pass


class ShellParserException(ConvertException):
    pass


class DockerfileGeneratorException(ConvertException):
    pass


class TPDockerfileGeneratorException(DockerfileGeneratorException):
    pass



