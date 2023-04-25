class ER7ExtractorError(Exception):
    pass


class MissingNHSNumberError(ER7ExtractorError):
    pass


class InvalidNHSNumberError(ER7ExtractorError):
    pass


class MissingPointOfCareError(ER7ExtractorError):
    pass


class MissingFacilityError(ER7ExtractorError):
    pass


class MissingPatientClassError(ER7ExtractorError):
    pass


class MissingAdmissionTypeError(ER7ExtractorError):
    pass


class MissingTimeOfAdmissionError(ER7ExtractorError):
    pass


class MissingFamilyNameError(ER7ExtractorError):
    pass


class MissingGivenNameError(ER7ExtractorError):
    pass
