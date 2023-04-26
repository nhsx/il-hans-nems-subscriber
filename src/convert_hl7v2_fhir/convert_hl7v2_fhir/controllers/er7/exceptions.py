class ER7ExtractorError(Exception):
    pass


class MissingFieldError(ER7ExtractorError):
    pass


class MissingNHSNumberError(MissingFieldError):
    pass


class InvalidNHSNumberError(ER7ExtractorError):
    pass


class MissingPointOfCareError(MissingFieldError):
    pass


class MissingFacilityError(MissingFieldError):
    pass


class MissingPatientClassError(MissingFieldError):
    pass


class MissingAdmissionTypeError(MissingFieldError):
    pass


class MissingTimeOfAdmissionError(MissingFieldError):
    pass


class MissingFamilyNameError(MissingFieldError):
    pass


class MissingGivenNameError(MissingFieldError):
    pass
