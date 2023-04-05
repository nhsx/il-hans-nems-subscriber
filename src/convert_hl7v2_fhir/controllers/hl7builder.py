from enum import Enum
from datetime import datetime
from typing import Optional, Literal
from uuid import uuid4

# enum of v2 error codes (from https://hl7-definition.caristix.com/v2/HL7v2.8/Tables/0357)
class v2ErrorCode(Enum):
    ACCEPTED = "0"
    SEGMENT_SEQUENCE_ERROR = "100"
    REQUIRED_FIELD_MISSING = "101"
    DATA_TYPE_ERROR = "102"
    TABLE_VALUE_NOT_FOUND = "103"
    VALUE_TOO_LONG = "104"
    UNSUPPORTED_MESSAGE_TYPE = "200"
    UNSUPPORTED_EVENT_CODE = "201"
    UNSUPPORTED_PROCESSING_ID = "202"
    UNSUPPORTED_VERSION_ID = "203"
    UNKNOWN_KEY_IDENTIFIER = "204"
    DUPLICATE_KEY_IDENTIFIER = "205"
    APPLICATION_RECORD_LOCKED = "206"
    APPLICATION_INTERNAL_ERROR = "207"

    def __str__(self):
        return self.value

# enum of v2 severity codes (from https://hl7-definition.caristix.com/v2/HL7v2.8/Tables/0516)
class v2ErrorSeverity(Enum):
    ERROR = "E"
    FATAL_ERROR = "F"
    INFORMATION = "I"
    WARNING = "W"

    def __str__(self):
        return self.value

def generate_MSH_segment(
    recipient_app: str,
    recipient_facility: str,
    message_control_id: Optional[str] = None
    ):
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    msg_id = message_control_id or uuid4()

    # see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/MSH
    return f"MSH|^~\\&|HANS|NHSENGLAND|{recipient_app}|{recipient_facility}|{timestamp}||ACK^A01|{msg_id}|||||||||||||||"


# for ACK message structure see: https://hl7-definition.caristix.com/v2/HL7v2.8/TriggerEvents/ACK
def generate_ACK_message(
    recipient_app: str,
    recipient_facility: str,
    replying_to_msgid: str,
    care_provider_email: Optional[str] = None,
    care_provider_orgname: Optional[str] = None,
    hl7_error_code: Optional[str] = None,
    error_severity: Optional[str] = None,
    error_message: Optional[str] = None
    ):

    segment_msh = generate_MSH_segment(recipient_app, recipient_facility)

    segment_err = ""
    segment_zha = ""
    accept_code = ""

    if hl7_error_code:
        # generate an ACK based on rejecting the message and processing no further
        accept_code = "AR"
        # for ERR layout, see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/ERR
        segment_err = f"\rERR|||{hl7_error_code}|{error_severity}||||{error_message}"
    else:
        # generate an ACK based on accepting the message and sending care provider email as response
        accept_code = "AA"
        if care_provider_email:
            # custom defined segment (see tech docs)
            segment_zha = f"\rZHA|{care_provider_orgname}|{care_provider_email}"
        
        
    # see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/MSA
    segment_msa = f"MSA|{accept_code}|{replying_to_msgid}"
    return segment_msh + "\r" + segment_msa + segment_err + segment_zha
