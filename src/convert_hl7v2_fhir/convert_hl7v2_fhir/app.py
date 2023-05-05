from datetime import date
from hashlib import scrypt
from typing import Optional

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from botocore.exceptions import ClientError, NoRegionError
from hl7apy.core import Message
from hl7apy.exceptions import ValidationError
from hl7apy.parser import parse_message

from convert_hl7v2_fhir.controllers.er7.er7_extractor import ER7Extractor
from convert_hl7v2_fhir.controllers.er7.er7_message_controller import (
    ER7MessageController,
)
from convert_hl7v2_fhir.controllers.er7.exceptions import (
    InvalidNHSNumberError,
    MissingNHSNumberError,
    MissingFieldError,
)
from convert_hl7v2_fhir.controllers.hl7.hl7_ack_builder import (
    generate_ack_message,
    HL7ErrorCode,
    HL7ErrorSeverity,
    HL7Error,
)
from convert_hl7v2_fhir.controllers.utils import hl7v2_lambda_response_factory
from convert_hl7v2_fhir.internal_integrations.management_interface.api_client import (
    ManagementInterfaceApiClient,
)
from convert_hl7v2_fhir.internal_integrations.management_interface.exceptions import (
    ManagementInterfaceApiClientException,
)
from convert_hl7v2_fhir.internal_integrations.sqs.settings import get_sqs_settings

_LOGGER = Logger()


@_LOGGER.inject_lambda_context(log_event=False)
def lambda_handler(event: dict, context: LambdaContext):
    er7_message = _parse_message(event["body"])

    try:
        if not _is_message_of_admit_discharge_transfer_type(er7_message):
            body = _create_ack_body(
                er7_message,
                HL7Error(
                    error_code=HL7ErrorCode.UNSUPPORTED_MESSAGE_TYPE,
                    error_severity=HL7ErrorSeverity.ERROR,
                    error_message="Only ADT message types are supported",
                ),
            )
            return hl7v2_lambda_response_factory(body=body)

        if not _is_message_of_admit_visit_event_code(er7_message):
            body = _create_ack_body(
                er7_message,
                HL7Error(
                    error_code=HL7ErrorCode.UNSUPPORTED_EVENT_CODE,
                    error_severity=HL7ErrorSeverity.ERROR,
                    error_message="Only A01 message event codes are supported",
                ),
            )
            return hl7v2_lambda_response_factory(body=body)

        if not _is_message_of_inpatient_visit_class(er7_message):
            body = _create_ack_body(
                er7_message,
                HL7Error(
                    error_code=HL7ErrorCode.APPLICATION_INTERNAL_ERROR,
                    error_severity=HL7ErrorSeverity.ERROR,
                    error_message="Only Inpatient visit patient class messages are supported",
                ),
            )
            return hl7v2_lambda_response_factory(body=body)

        if not _is_patient_added_to_hans(er7_message):
            body = _create_ack_body(er7_message)
            return hl7v2_lambda_response_factory(body=body)

        er7_extractor = ER7Extractor(er7_message)
        fhir_bundle = ER7MessageController(er7_extractor=er7_extractor).to_fhir_bundle()
        _send_to_sqs(fhir_bundle.json())
        _LOGGER.info("Successfully processed message")
    except ValidationError as ex:
        # Malformed message, not adhering to the structures defined by HL7
        _LOGGER.exception(str(ex))
        body = _create_ack_body(
            er7_message,
            HL7Error(
                error_code=HL7ErrorCode.SEGMENT_SEQUENCE_ERROR,
                error_severity=HL7ErrorSeverity.ERROR,
                error_message=str(ex),
            ),
        )
        return hl7v2_lambda_response_factory(body=body)

    except InvalidNHSNumberError as ex:
        _LOGGER.exception(str(ex))
        body = _create_ack_body(
            er7_message,
            HL7Error(
                error_code=HL7ErrorCode.DATA_TYPE_ERROR,
                error_severity=HL7ErrorSeverity.ERROR,
                error_message="NHS Number in message was invalid",
            ),
        )
        return hl7v2_lambda_response_factory(body=body)

    except MissingNHSNumberError as ex:
        _LOGGER.exception(str(ex))
        body = _create_ack_body(
            er7_message,
            HL7Error(
                error_code=HL7ErrorCode.UNKNOWN_KEY_IDENTIFIER,
                error_severity=HL7ErrorSeverity.ERROR,
                error_message="NHS Number missing from message",
            ),
        )
        return hl7v2_lambda_response_factory(body=body)

    except MissingFieldError as ex:
        _LOGGER.exception(str(ex))
        body = _create_ack_body(
            er7_message,
            HL7Error(
                error_code=HL7ErrorCode.REQUIRED_FIELD_MISSING,
                error_severity=HL7ErrorSeverity.ERROR,
                error_message=str(ex),
            ),
        )
        return hl7v2_lambda_response_factory(body=body)

    except (ClientError, NoRegionError) as ex:
        _LOGGER.exception(str(ex))
        body = _create_ack_body(
            er7_message,
            HL7Error(
                error_code=HL7ErrorCode.APPLICATION_INTERNAL_ERROR,
                error_severity=HL7ErrorSeverity.ERROR,
                error_message="Issue reaching SQS service: " + str(ex),
            ),
        )
        return hl7v2_lambda_response_factory(body=body)

    except Exception as ex:
        _LOGGER.exception(str(ex))
        body = _create_ack_body(
            er7_message,
            HL7Error(
                error_code=HL7ErrorCode.APPLICATION_INTERNAL_ERROR,
                error_severity=HL7ErrorSeverity.FATAL_ERROR,
                error_message=str(ex),
            ),
        )
        return hl7v2_lambda_response_factory(body=body)

    return hl7v2_lambda_response_factory(body=_create_ack_body(er7_message))


def _send_to_sqs(body: str):
    sqs = client("sqs")
    sqs_settings = get_sqs_settings()
    sqs.send_message(QueueUrl=sqs_settings.converted_queue_url, MessageBody=body)


def _create_ack_body(
    er7_message: Message,
    hl7_error: Optional[HL7Error] = None,
) -> str:
    sending_application = er7_message.msh.sending_application.value
    sending_facility = er7_message.msh.sending_facility.value
    msg_control_id = er7_message.msh.message_control_id.value
    return generate_ack_message(
        receiving_application=sending_application,
        receiving_facility=sending_facility,
        replying_to_msgid=msg_control_id,
        hl7_error=hl7_error,
    )


def _parse_message(body: str) -> Message:
    # hl7 messages expect \r rather than \r\n (and the parsing library)
    #  will reject otherwise (with a KeyError)
    return parse_message(body.replace("\n", ""))


def _is_message_of_admit_discharge_transfer_type(er7_message: Message) -> bool:
    return ER7Extractor(er7_message=er7_message).message_type() == "ADT"


def _is_message_of_admit_visit_event_code(er7_message: Message) -> bool:
    return ER7Extractor(er7_message=er7_message).trigger_event() == "A01"


def _is_message_of_inpatient_visit_class(er7_message: Message) -> bool:
    return ER7Extractor(er7_message=er7_message).patient_class() == "I"


def _is_patient_added_to_hans(er7_message: Message) -> bool:
    def _generate_pseudo_id(nhs_number: str, birth_date: date) -> str:
        # https://nhsx.github.io/il-hans-infrastructure/adrs/003-Do-not-use-NEMS-or-MESH
        return scrypt(
            nhs_number.encode(),
            salt=str(birth_date).encode(),
            n=32768,
            r=12,
            p=6,
            maxmem=2**26,
        ).hex()

    extractor = ER7Extractor(er7_message=er7_message)
    management_interface_api_client = ManagementInterfaceApiClient()
    care_recipient_pseudo_id = _generate_pseudo_id(
        extractor.nhs_number(), extractor.date_of_birth()
    )
    try:
        management_interface_api_client.get_care_provider(
            care_recipient_pseudo_id=care_recipient_pseudo_id
        )
    except ManagementInterfaceApiClientException:
        return False

    return True
