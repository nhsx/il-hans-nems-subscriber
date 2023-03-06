class VerifyPatientException(Exception):
    pass


class NameMissmatch(VerifyPatientException):
    pass


class BirthDateMissmatch(VerifyPatientException):
    pass
