from hl7 import Message

from exceptions import InvalidNHSNumber, MissingNHSNumber
from datetime import datetime
from typing import Union
from uuid import uuid4

# note - this is pilot partner specific
#  so will need implementing with our pilot
#  partner in mind
ADMISSION_METHOD_MAP = {
    "28b": {
        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AdmissionMethodEngland",
        "code": "28"
    }
}

# from HL7v2 to FHIR conversion map for encounter class
# at https://docs.google.com/spreadsheets/d/1T8Q6rSolB8lh56sXr3SVZ6AAPQGqD8D0zCoxz2dzdkM/edit#gid=0
ENCOUNTER_CLASS_MAP = {
    "E": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "EMER",
        "display": "emergency"
    },
    "I": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "IMP",
        "display": "inpatient encounter"
    },
    "O": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "AMB",
        "display": "ambulatory"
    },
    "P": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "PRENC",
        "display": "pre-admission"
    },
    "R": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "R",
        "display": "Recurring patient"
    },
    "B": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "B",
        "display": "Obstetrics"
    },
    "C": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "C",
        "display": "Commercial Account"
    },
    "N": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "N",
        "display": "Not Applicable"
    },
    "U": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "U",
        "display": "Unknown"
    }
}

def get(msg: Message, 
            segment_type: str,
            segment_repetition: int = 0,
            field: int = None,
            repetition : int = None,
            component : int = None,
            sub_component: int = None):
        
        seg = msg.segments(segment_type)[segment_repetition]
        if field is None:
            return seg
        else:
            fld = seg[field]
            if repetition is None:
                return fld
            else:
                rep = fld[repetition]
                if component is None:
                    return rep
                else:
                    cmp = rep[component]
                    if sub_component is None:
                        return cmp
                    else:
                        sub_cmp = cmp[sub_component]
                        return sub_cmp if sub_cmp != "" else None

def get_str(msg: Message, 
        segment_type: str,
        segment_repetition: int = 0,
        field: int = None,
        repetition : int = None,
        component : int = None,
        sub_component: int = None) -> Union[None, str]:
        
        ret = get(msg, segment_type, segment_repetition, field, repetition, component, sub_component)

        return str(ret) if str(ret) != "" else None

def get_nhs_number(msg: Message):
        # gets the list of identifiers
        ids = list(get(msg, "PID", 0, 3))

        # also add on the single ID that may proceed it (if it exists and is not in list)
        if get(msg, "PID", 0, 2, 0):
            ids.append(get(msg, "PID", 0, 2, 0))

        for id in ids:
            if id[4][0] == "NHSNMBR":
                nhs_num = id[0][0]
                if not is_nhs_number_valid(nhs_num):
                    raise InvalidNHSNumber
                else:
                    return nhs_num
        
        # if none match that criteria
        raise MissingNHSNumber

def is_nhs_number_valid(nhs_number : str) -> bool:
    # check length
    if len(nhs_number) != 10:
        return False
    
    # perform modulus 11 check (see https://www.datadictionary.nhs.uk/attributes/nhs_number.html)
    check_digit = nhs_number[9]
    main_part = nhs_number[0:9]
    
    sum = 0
    for digit_index in range(0, 9):
        sum += (10 - digit_index) * int(main_part[digit_index])
    calculated_check_digit = 11 - (sum % 11)

    if calculated_check_digit == 10:
        return False
    elif calculated_check_digit == 11:
        calculated_check_digit = 0
    
    return (str(calculated_check_digit) == check_digit)
        

def to_fhir_date(hl7_DTM : str):
    if (len(hl7_DTM) > 8):
        hl7_DTM = hl7_DTM[:8]
    
    return (hl7_DTM[0:4] + "-" + hl7_DTM[4:6] + "-" + hl7_DTM[6:8])

def to_fhir_datetime(hl7_DTM):
    if (len(hl7_DTM) <= 8):
        raise Exception # TODO: Replace this

    return to_fhir_date(hl7_DTM) + "T" + hl7_DTM[8:10] + ":" + hl7_DTM[10:12] + ":" + hl7_DTM[12:14] + "Z"
    
def to_fhir_admission_method(hl7_CWE):
    return ADMISSION_METHOD_MAP[hl7_CWE]

def to_fhir_encounter_class(hl7_CWE):
    return ENCOUNTER_CLASS_MAP[hl7_CWE]


def generate_MSH_segment(
    recipient_app: str,
    recipient_facility: str,
    ):
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    msg_id = uuid4()

    # see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/MSH
    return f"MSH|^~\&|HANS|NHSENGLAND|{recipient_app}|{recipient_facility}|{timestamp}||ACK^A01|{msg_id}|||||||||||||||"


# for ACK message structure see: https://hl7-definition.caristix.com/v2/HL7v2.8/TriggerEvents/ACK
def generate_ACK_message(
    recipient_app: str,
    recipient_facility: str,
    replying_to_msgid: str,
    care_provider_email: str = None,
    care_provider_orgname: str = None,
    hl7_error_code: str = None,
    error_message: str = None
    ):

    segment_msh = generate_MSH_segment(recipient_app, recipient_facility)

    segment_err = ""
    segment_zha = ""
    accept_code = ""

    if not hl7_error_code:
        accept_code = "AA"
        # custom defined segment (see tech docs)
        segment_zha = f"\nZHA|{care_provider_orgname}|{care_provider_email}"
    else:
        accept_code = "AR"
        # see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/ERR
        segment_err = f"\nERR|||{hl7_error_code}|E||||{error_message}"
        
    # see https://hl7-definition.caristix.com/v2/HL7v2.8/Segments/MSA
    segment_msa = f"MSA|{accept_code}|{replying_to_msgid}"
    return segment_msh + "\n" + segment_msa + segment_err + segment_zha


print(generate_ACK_message(
    recipient_app="HOMERTON_TIE",
    recipient_facility="HOMERTON",
    replying_to_msgid="MSG00001",
    hl7_error_code="101",
    error_message="Missing NHS Number") + "\n")
print(generate_ACK_message(
    recipient_app="HOMERTON_TIE",
    recipient_facility="HOMERTON",
    care_provider_email="test@nhs.net",
    care_provider_orgname="Test Care Provider - Reading Branch",
    replying_to_msgid="MSG00002"))