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


class ExampleBasedMatcherException(TaskMatcherException):
    pass


class AnsiblePlayContextException(BaseException):
    pass


class RoleGeneratorException(BaseException):
    pass
