from uuid import uuid4

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue

from controllers.exceptions import (
    IncorrectNHSNumber,
    PatientNotFound,
    InternalError,
    BirthDateMissmatch,
    NameMissmatch,
)
from controllers.verify_patient import VerifyPatientController
from pydantic import ValidationError

from schemas import HANSPatient

_LOGGER = Logger()


@_LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    try:
        patient = HANSPatient.parse_raw(event["body"])
        VerifyPatientController().verify_patient_data(
            nhs_number=patient.identifier[0].value,
            patient_name=patient.name[0],
            birth_date=patient.birthDate,
        )
    except ValidationError as ex:
        return {
            "statusCode": 400,
            "body": OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="value",
                        diagnostics=str(ex),
                    )
                ]
            ).json(),
        }
    except IncorrectNHSNumber:
        return {
            "statusCode": 400,
            "body": OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="value",
                        diagnostics="NHS Number provided was invalid",
                    )
                ]
            ).json(),
        }
    except (BirthDateMissmatch, NameMissmatch) as ex:
        return {
            "statusCode": 400,
            "body": OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="business-rule",
                        diagnostics=f"Provided data is incorrect: {type(ex).__name__}",
                    )
                ]
            ).json(),
        }
    except PatientNotFound:
        return {
            "statusCode": 404,
            "body": OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="not-found",
                        diagnostics="NHS Number did not exist on PDS",
                    )
                ]
            ).json(),
        }
    except InternalError:
        return {
            "statusCode": 500,
            "body": OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="exception",
                        diagnostics="Unknown error occurred",
                    )
                ]
            ).json(),
        }
    return {"statusCode": 201, "headers": {"X-Subscription-Id": str(uuid4())}}
