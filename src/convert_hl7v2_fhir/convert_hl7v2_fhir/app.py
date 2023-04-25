from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from boto3 import client
from botocore.exceptions import ClientError, NoRegionError
import hl7

from convert_hl7v2_fhir.controllers.hl7builder import (
    generate_ACK_message,
    v2ErrorCode,
    v2ErrorSeverity,
)
from convert_hl7v2_fhir.controllers.convertor import HL7v2ConversionController
from convert_hl7v2_fhir.controllers.exceptions import (
    InvalidNHSNumberError,
    MissingNHSNumberError,
    MissingFieldOrComponentError,
    MissingSegmentError,
)
from convert_hl7v2_fhir.internal_integrations.sqs.settings import SQSSettings

_LOGGER = Logger()


def lambda_handler(event: dict, context: LambdaContext):
    body = str(event["body"])

    # hl7 messages expect \r rather than \r\n (and the parsing library)
    #  will reject otherwise (with a KeyError)
    msg_parsed = hl7.parse(body.replace("\n", ""))

    ack = _create_ack(msg_parsed)

    try:
        fhir_json = _convert(msg_parsed)
        _send_to_sqs(fhir_json)
        _LOGGER.info("Successfully processed message")
    except InvalidNHSNumberError as ex:
        _LOGGER.error(ex)
        ack = _create_nak(
            msg_parsed,
            v2ErrorCode.DATA_TYPE_ERROR,
            v2ErrorSeverity.ERROR,
            "NHS Number in message was invalid",
        )
    except MissingNHSNumberError as ex:
        _LOGGER.error(ex)
        ack = _create_nak(
            msg_parsed,
            v2ErrorCode.UNKNOWN_KEY_IDENTIFIER,
            v2ErrorSeverity.ERROR,
            "NHS Number missing from message",
        )
    except MissingSegmentError as ex:
        _LOGGER.error(ex)
        ack = _create_nak(
            msg_parsed,
            v2ErrorCode.SEGMENT_SEQUENCE_ERROR,
            v2ErrorSeverity.ERROR,
            "Required segment was missing: " + str(ex),
        )
    except MissingFieldOrComponentError as ex:
        _LOGGER.error(ex)
        ack = _create_nak(
            msg_parsed,
            v2ErrorCode.REQUIRED_FIELD_MISSING,
            v2ErrorSeverity.ERROR,
            "Required field was missing: " + str(ex),
        )
    except (ClientError, NoRegionError) as ex:
        _LOGGER.error(ex)
        ack = _create_nak(
            msg_parsed,
            v2ErrorCode.APPLICATION_INTERNAL_ERROR,
            v2ErrorSeverity.ERROR,
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
        "body": ack,
    }


def _send_to_sqs(body: str):
    sqs = client("sqs")
    sqs_settings = SQSSettings()
    sqs.send_message(QueueUrl=sqs_settings.converted_queue_url, MessageBody=body)


def _create_nak(
    msg_parsed: hl7.Message, err_code: str, err_sev: str, err_msg: str
) -> str:
    sending_app = msg_parsed["MSH"][0][3][0]
    sending_facility = msg_parsed["MSH"][0][4][0]
    msg_control_id = msg_parsed["MSH"][0][10][0]
    return generate_ACK_message(
        recipient_app=sending_app,
        recipient_facility=sending_facility,
        replying_to_msgid=msg_control_id,
        hl7_error_code=err_code,
        error_severity=err_sev,
        error_message=err_msg,
    )


def _create_ack(msg_parsed: hl7.Message) -> str:
    sending_app = msg_parsed["MSH"][0][3][0]
    sending_facility = msg_parsed["MSH"][0][4][0]
    msg_control_id = msg_parsed["MSH"][0][10][0]
    return generate_ACK_message(
        recipient_app=sending_app,
        recipient_facility=sending_facility,
        replying_to_msgid=msg_control_id,
    )


def _convert(v2msg: str) -> str:
    convertor = HL7v2ConversionController()
    return convertor.convert(v2msg)
