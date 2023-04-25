class VerifyPatientException(Exception):
    pass


class NameMissmatch(VerifyPatientException):
    pass


class BirthDateMissmatch(VerifyPatientException):
    pass


class IncorrectNHSNumber(VerifyPatientException):
    pass


class PatientNotFound(VerifyPatientException):
    pass


class InternalError(VerifyPatientException):
    pass
