from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from botocore.exceptions import ClientError, NoRegionError
from hl7apy.core import Message
from hl7apy.exceptions import ValidationError
from hl7apy.parser import parse_message

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
)
from convert_hl7v2_fhir.internal_integrations.sqs.settings import get_sqs_settings

_LOGGER = Logger()


def lambda_handler(event: dict, context: LambdaContext):
    body = str(event["body"])

    # hl7 messages expect \r rather than \r\n (and the parsing library)
    #  will reject otherwise (with a KeyError)
    er7_message = parse_message(body.replace("\n", ""))

    ack_message = _create_ack_message(er7_message)

    try:
        fhir_bundle = ER7MessageController(er7_message).to_fhir_bundle()
        _send_to_sqs(fhir_bundle.json())
        _LOGGER.info("Successfully processed message")
    except ValidationError as ex:
        # Malformed message, not adhering to the structures defined by HL7
        _LOGGER.exception(str(ex))
        ack_message = _create_nak(
            er7_message,
            HL7ErrorCode.SEGMENT_SEQUENCE_ERROR,
            HL7ErrorSeverity.ERROR,
            str(ex),
        )
    except InvalidNHSNumberError as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            er7_message,
            HL7ErrorCode.DATA_TYPE_ERROR,
            HL7ErrorSeverity.ERROR,
            "NHS Number in message was invalid",
        )
    except MissingNHSNumberError as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            er7_message,
            HL7ErrorCode.UNKNOWN_KEY_IDENTIFIER,
            HL7ErrorSeverity.ERROR,
            "NHS Number missing from message",
        )

    except MissingFieldError as ex:
        _LOGGER.exception(str(ex))
        ack_message = _create_nak(
            er7_message,
            HL7ErrorCode.REQUIRED_FIELD_MISSING,
            HL7ErrorSeverity.ERROR,
            str(ex),
        )

    except (ClientError, NoRegionError) as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            er7_message,
            HL7ErrorCode.APPLICATION_INTERNAL_ERROR,
            HL7ErrorSeverity.ERROR,
            "Issue reaching SQS service: " + str(ex),
        )

    except Exception as ex:
        # though this is generally bad practice, we need to
        #  return an ERR response over HL7v2 for all cases
        #  otherwise hospital system will not know we have had
        #  an internal server error - we will log as error though
        _LOGGER.error(ex)
        ack_message = _create_nak(
            er7_message,
            HL7ErrorCode.APPLICATION_INTERNAL_ERROR,
            HL7ErrorSeverity.FATAL_ERROR,
            str(ex),
        )

    return {
        "statusCode": 200,
        "headers": {"content-type": "x-application/hl7-v2+er; charset=utf-8"},
        "body": ack_message,
    }


def _send_to_sqs(body: str):
    sqs = client("sqs")
    sqs_settings = get_sqs_settings()
    sqs.send_message(QueueUrl=sqs_settings.converted_queue_url, MessageBody=body)


def _create_nak(
    er7_message: Message,
    error_code: HL7ErrorCode,
    error_severity: HL7ErrorSeverity,
    err_msg: str,
) -> str:
    sending_application = er7_message.msh.sending_application.value
    sending_facility = er7_message.msh.sending_facility.value
    msg_control_id = er7_message.msh.message_control_id.value
    return generate_ack_message(
        receiving_application=sending_application,
        receiving_facility=sending_facility,
        replying_to_msgid=msg_control_id,
        hl7_error_code=error_code,
        error_severity=error_severity,
        error_message=err_msg,
    )


def _create_ack_message(er7_message: Message) -> str:
    sending_application = er7_message.msh.sending_application.value
    sending_facility = er7_message.msh.sending_facility.value
    msg_control_id = er7_message.msh.message_control_id.value
    return generate_ack_message(
        receiving_application=sending_application,
        receiving_facility=sending_facility,
        replying_to_msgid=msg_control_id,
    )
