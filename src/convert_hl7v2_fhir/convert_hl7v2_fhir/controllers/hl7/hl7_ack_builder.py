from datetime import datetime
from enum import Enum, IntEnum
from typing import Optional
from uuid import uuid4, UUID

from pydantic import BaseModel


class HL7ErrorCode(IntEnum):
    """https://hl7-definition.caristix.com/v2/HL7v2.8/Tables/0357"""

    ACCEPTED = 0
    SEGMENT_SEQUENCE_ERROR = 100
    REQUIRED_FIELD_MISSING = 101
    DATA_TYPE_ERROR = 102
    TABLE_VALUE_NOT_FOUND = 103
    VALUE_TOO_LONG = 104
    UNSUPPORTED_MESSAGE_TYPE = 200
    UNSUPPORTED_EVENT_CODE = 201
    UNSUPPORTED_PROCESSING_ID = 202
    UNSUPPORTED_VERSION_ID = 203
    UNKNOWN_KEY_IDENTIFIER = 204
    DUPLICATE_KEY_IDENTIFIER = 205
    APPLICATION_RECORD_LOCKED = 206
    APPLICATION_INTERNAL_ERROR = 207


class HL7ErrorSeverity(str, Enum):
    """https://hl7-definition.caristix.com/v2/HL7v2.8/Tables/0516"""

    ERROR = "E"
    FATAL_ERROR = "F"
    INFORMATION = "I"
    WARNING = "W"


class HL7Error(BaseModel):
    error_code: HL7ErrorCode
    error_severity: HL7ErrorSeverity
    error_message: str


def generate_ack_message(
    receiving_application: str,
    receiving_facility: str,
    replying_to_msgid: str,
    care_provider_email: Optional[str] = None,
    care_provider_orgname: Optional[str] = None,
    hl7_error: Optional[HL7Error] = None,
):
    """https://hl7-definition.caristix.com/v2/HL7v2.8/TriggerEvents/ACK"""

    message_header = _generate_msh_segment(receiving_application, receiving_facility)

    segment_err = ""
    segment_zha = ""
    accept_code = ""

    if hl7_error is not None:
        # generate an ACK based on rejecting the message and processing no further
        accept_code = "AR"
        # for ERR layout, see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/ERR
        segment_err = f"\rERR|||{hl7_error.error_code}|{hl7_error.error_severity}||||{hl7_error.error_message}"
    else:
        # generate an ACK based on accepting the message and sending care provider email as response
        accept_code = "AA"
        if care_provider_email:
            # custom defined segment (see tech docs)
            segment_zha = f"\rZHA|{care_provider_orgname}|{care_provider_email}"

    # see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/MSA
    segment_msa = f"MSA|{accept_code}|{replying_to_msgid}"
    return message_header + "\r" + segment_msa + segment_err + segment_zha


def _generate_msh_segment(
    receiving_application: str,
    receiving_facility: str,
    message_control_id: Optional[UUID] = None,
):
    """https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/MSH"""

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    msg_id = message_control_id or uuid4()
    return f"MSH|^~\\&|HANS|NHSENGLAND|{receiving_application}|{receiving_facility}|{timestamp}||ACK^A01|{msg_id}|||||||||||||||"


def _generate_msa_segment(
    accept_code: str,
    message_control_id: str,
):
    """https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/MSA"""

    return f"MSA|{accept_code}|{message_control_id}"


def _generate_err_segment(
    error_code: HL7ErrorCode,
    error_severity: HL7ErrorSeverity,
    error_message: str,
):
    """https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/ERR"""

    return f"ERR|||{error_code}|{error_severity}||||{error_message}"


def _generate_zha_segment(
    care_provider_orgname: str,
    care_provider_email: str,
):
    """custom defined segment (see tech docs)"""

    return f"ZHA|{care_provider_orgname}|{care_provider_email}"
