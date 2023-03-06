class VerifyPatientException(Exception):
    pass


class NameMissmatchError(VerifyPatientException):
    pass


class BirthDateMissmatchError(VerifyPatientException):
    pass


class NotOKResponseFromPDSError(VerifyPatientException):
    pass
