import hl7
from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from botocore.exceptions import ClientError, NoRegionError

from convert_hl7v2_fhir.controllers.hl7.exceptions import (
    InvalidNHSNumberError,
    MissingNHSNumberError,
    MissingFieldOrComponentError,
    MissingSegmentError,
)
from convert_hl7v2_fhir.controllers.hl7.hl7_builder import (
    HL7ErrorCode,
    HL7ErrorSeverity,
    generate_ack_message,
)
from convert_hl7v2_fhir.controllers.hl7.hl7_message_controller import (
    HL7MessageController,
)
from convert_hl7v2_fhir.controllers.hl7builder import (
    v2ErrorCode,
    v2ErrorSeverity,
)
from convert_hl7v2_fhir.internal_integrations.sqs.settings import get_sqs_settings

_LOGGER = Logger()


def lambda_handler(event: dict, context: LambdaContext):
    body = str(event["body"])

    # hl7 messages expect \r rather than \r\n (and the parsing library)
    #  will reject otherwise (with a KeyError)
    hl7_message = hl7.parse(body.replace("\n", ""))

    ack_message = _create_ack_message(hl7_message)

    try:
        fhir_bundle = HL7MessageController(hl7_message).to_fhir_bundle()
        _send_to_sqs(fhir_bundle.json())
        _LOGGER.info("Successfully processed message")
    except InvalidNHSNumberError as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            hl7_message,
            HL7ErrorCode.DATA_TYPE_ERROR,
            HL7ErrorSeverity.ERROR,
            "NHS Number in message was invalid",
        )
    except MissingNHSNumberError as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            hl7_message,
            HL7ErrorCode.UNKNOWN_KEY_IDENTIFIER,
            HL7ErrorSeverity.ERROR,
            "NHS Number missing from message",
        )
    except MissingSegmentError as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            hl7_message,
            HL7ErrorCode.SEGMENT_SEQUENCE_ERROR,
            HL7ErrorSeverity.ERROR,
            "Required segment was missing: " + str(ex),
        )
    except MissingFieldOrComponentError as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            hl7_message,
            HL7ErrorCode.REQUIRED_FIELD_MISSING,
            HL7ErrorSeverity.ERROR,
            "Required field was missing: " + str(ex),
        )
    except (ClientError, NoRegionError) as ex:
        _LOGGER.error(ex)
        ack_message = _create_nak(
            hl7_message,
            HL7ErrorCode.APPLICATION_INTERNAL_ERROR,
            HL7ErrorSeverity.ERROR,
            "Issue reaching SQS service: " + str(ex),
        )
    except Exception as ex:
        # though this is generally bad practice, we need to
        #  return an ERR response over HL7v2 for all cases
        #  otherwise hospital system will not know we have had
        #  an internal server error - we will log as error though
        _LOGGER.exception(ex)
        ack = _create_nak(
            msg_parsed,
            v2ErrorCode.APPLICATION_INTERNAL_ERROR,
            v2ErrorSeverity.FATAL_ERROR,
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
    hl7_message: hl7.Message,
    error_code: HL7ErrorCode,
    error_severity: HL7ErrorSeverity,
    err_msg: str,
) -> str:
    sending_application = hl7_message.extract_field("MSH", 0, 3, 0)
    sending_facility = hl7_message.extract_field("MSH", 0, 4, 0)
    msg_control_id = hl7_message.extract_field("MSH", 0, 10, 0)
    return generate_ack_message(
        receiving_application=sending_application,
        receiving_facility=sending_facility,
        replying_to_msgid=msg_control_id,
        hl7_error_code=error_code,
        error_severity=error_severity,
        error_message=err_msg,
    )


def _create_ack_message(hl7_message: hl7.Message) -> str:
    sending_application = hl7_message.extract_field("MSH", 0, 3, 0)
    sending_facility = hl7_message.extract_field("MSH", 0, 4, 0)
    msg_control_id = hl7_message.extract_field("MSH", 0, 10, 0)
    return generate_ack_message(
        receiving_application=sending_application,
        receiving_facility=sending_facility,
        replying_to_msgid=msg_control_id,
    )
