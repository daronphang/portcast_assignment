class CustomException(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message)


class BadRequest(CustomException):
    STATUS_CODE = 400
    pass


class DBFailure(CustomException):
    STATUS_CODE = 400
    pass


class MissingSchema(CustomException):
    STATUS_CODE = 400
    pass


class InvalidField(CustomException):
    STATUS_CODE = 400
    pass


class MissingKey(CustomException):
    STATUS_CODE = 400
    pass

