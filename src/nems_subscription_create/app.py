from uuid import uuid4

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.patient import Patient

from controllers.exceptions import (
    NameMissmatchError,
    BirthDateMissmatchError,
    NotOKResponseFromPDSError,
)
from controllers.verify_patient import VerifyPatientController

_LOGGER = Logger()


@_LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    patient = Patient.parse_raw(event["body"])
    try:
        VerifyPatientController().verify_patient_data(
            nhs_number=patient.identifier[0].value,
            family_name=patient.name[0].family,
            given_name=patient.name[0].given,
            birth_date=patient.birthDate,
        )
    except NotOKResponseFromPDSError:
        return {"statusCode": 502}
    except (NameMissmatchError, BirthDateMissmatchError):
        return {"statusCode": 404}
    return {"statusCode": 201, "headers": {"X-Subscription-Id": str(uuid4())}}
