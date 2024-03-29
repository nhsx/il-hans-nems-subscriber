from uuid import uuid4

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import ValidationError
from pydantic.env_settings import SettingsError
from urllib3.exceptions import MaxRetryError

from subscription_create.controllers.exceptions import (
    IncorrectNHSNumber,
    PatientNotFound,
    InternalError,
    BirthDateMissmatch,
    NameMissmatch,
)
from subscription_create.controllers.verify_patient import VerifyPatientController
from subscription_create.schemas import HANSPatient
from subscription_create.utils import operation_outcome_lambda_response_factory

_LOGGER = Logger()
verify_patient_controller = VerifyPatientController()


@_LOGGER.inject_lambda_context(log_event=False)
def lambda_handler(event: dict, context: LambdaContext):
    try:
        patient = HANSPatient.parse_raw(event["body"])
        verify_patient_controller.verify_patient_data(
            nhs_number=patient.identifier[0].value,
            patient_name=patient.name[0],
            birth_date=patient.birthDate,
        )
        return {"statusCode": 201, "headers": {"X-Subscription-Id": str(uuid4())}}
    except ValidationError as ex:
        return operation_outcome_lambda_response_factory(
            status_code=400, severity="error", code="value", diagnostics=str(ex)
        )
    except IncorrectNHSNumber:
        return operation_outcome_lambda_response_factory(
            status_code=400,
            severity="error",
            code="value",
            diagnostics="NHS Number provided was invalid",
        )
    except BirthDateMissmatch:
        return operation_outcome_lambda_response_factory(
            status_code=400,
            severity="error",
            code="business-rule",
            diagnostics="Date of birth did not match",
        )
    except NameMissmatch:
        return operation_outcome_lambda_response_factory(
            status_code=400,
            severity="error",
            code="business-rule",
            diagnostics="Name did not match",
        )
    except PatientNotFound:
        return operation_outcome_lambda_response_factory(
            status_code=404,
            severity="error",
            code="not-found",
            diagnostics="NHS Number did not exist on PDS",
        )
    except (MaxRetryError, InternalError) as ex:
        _LOGGER.exception(str(ex))
        return operation_outcome_lambda_response_factory(
            status_code=500,
            severity="error",
            code="exception",
            diagnostics="Unknown error occurred",
        )
    except SettingsError as ex:
        return operation_outcome_lambda_response_factory(
            status_code=500,
            severity="exception",
            code="value",
            diagnostics=str(ex),
        )
