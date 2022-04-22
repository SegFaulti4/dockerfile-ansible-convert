class ConvertException(Exception):
    pass


class BashlexParsingException(ConvertException):
    pass


class EnrichCommandException(ConvertException):
    pass


class GenerateAnsibleASTException(ConvertException):
    pass


class DockerfileStackException(GenerateAnsibleASTException):
    pass


class MatchAnsibleModuleException(ConvertException):
    pass


class TestException(Exception):
    pass


class AnsibleCheckException(TestException):
    pass


class CloudException(TestException):
    pass
