from enum import Enum

from aws_lambda_powertools import Logger
from fhir.resources.operationoutcome import OperationOutcome

_LOGGER = Logger()


class PDSApiClientException(Exception):
    pass


class InvalidNHSNumber(PDSApiClientException):
    pass


class MissingNHSNumber(PDSApiClientException):
    pass


class PatientDoesNotExist(PDSApiClientException):
    pass


class PatientDidButNoLongerExists(PDSApiClientException):
    pass


class UnknownPDSError(PDSApiClientException):
    pass


class PDSUnavailable(PDSApiClientException):
    pass


class PDSApiErrorCode(str, Enum):
    INVALID_RESOURCE_ID = "INVALID_RESOURCE_ID"
    UNSUPPORTED_SERVICE = "UNSUPPORTED_SERVICE"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    INVALIDATED_RESOURCE = "INVALIDATED_RESOURCE"


def operation_outcome_to_exception(operation_outcome: OperationOutcome):
    issue_error_code = operation_outcome.issue[0].details.coding[0].code
    if issue_error_code == PDSApiErrorCode.INVALID_RESOURCE_ID:
        raise InvalidNHSNumber

    if issue_error_code == PDSApiErrorCode.UNSUPPORTED_SERVICE:
        raise MissingNHSNumber

    if issue_error_code == PDSApiErrorCode.RESOURCE_NOT_FOUND:
        raise PatientDoesNotExist

    if issue_error_code == PDSApiErrorCode.INVALIDATED_RESOURCE:
        raise PatientDidButNoLongerExists

    _LOGGER.warning("Raising unknown PDS error: %s", issue_error_code)
    raise UnknownPDSError
