class ConvertException(Exception):
    pass


class BashlexParsingException(ConvertException):
    pass


class EnrichCommandException(ConvertException):
    pass


class GenerateAnsibleASTException(ConvertException):
    pass
