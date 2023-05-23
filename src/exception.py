class BaseException(Exception):
    pass


class ShellParserException(BaseException):
    pass


class BashlexShellParserException(ShellParserException):
    pass


class DockerfileParserException(BaseException):
    pass


class TPDockerfileParserException(DockerfileParserException):
    pass


class TaskMatcherException(BaseException):
    pass


class CommandConfigLoaderException(TaskMatcherException):
    pass
