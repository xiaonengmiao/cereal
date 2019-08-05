class CerealException(Exception):
    pass


class NetworkException(CerealException):
    pass


class NotSyncingError(CerealException):
    pass


class NotMintingError(CerealException):
    pass


class BelowExpectError(CerealException):
    pass
