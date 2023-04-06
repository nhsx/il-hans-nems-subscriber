from typing import Optional

from controllers.exceptions import MissingFieldOrComponentError

# note - this is pilot partner specific
#  so will need implementing with our pilot
#  partner in mind
ADMISSION_METHOD_MAP = {
    "28b": {
        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AdmissionMethodEngland",
        "code": "28",
    }
}

# from HL7v2 to FHIR conversion map for encounter class
# at https://docs.google.com/spreadsheets/d/1T8Q6rSolB8lh56sXr3SVZ6AAPQGqD8D0zCoxz2dzdkM/edit#gid=0
ENCOUNTER_CLASS_MAP = {
    "E": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "EMER",
        "display": "emergency",
    },
    "I": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "IMP",
        "display": "inpatient encounter",
    },
    "O": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "AMB",
        "display": "ambulatory",
    },
    "P": {
        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
        "code": "PRENC",
        "display": "pre-admission",
    },
    "R": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "R",
        "display": "Recurring patient",
    },
    "B": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "B",
        "display": "Obstetrics",
    },
    "C": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "C",
        "display": "Commercial Account",
    },
    "N": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "N",
        "display": "Not Applicable",
    },
    "U": {
        "system": "http://terminology.hl7.org/CodeSystem/v2-0004",
        "code": "U",
        "display": "Unknown",
    },
}


def to_fhir_date(hl7_DTM: Optional[str]) -> str:
    if len(hl7_DTM) > 8:
        hl7_DTM = hl7_DTM[:8]

    return hl7_DTM[0:4] + "-" + hl7_DTM[4:6] + "-" + hl7_DTM[6:8]


def to_fhir_datetime(hl7_DTM: str) -> str:
    if len(hl7_DTM) != 14:
        raise ValueError(
            "Expected HL7v2 DTM (with time) of length 14 but recieved length "
            + str(len(hl7_DTM))
            + " instead"
        )

    return (
        to_fhir_date(hl7_DTM)
        + "T"
        + hl7_DTM[8:10]
        + ":"
        + hl7_DTM[10:12]
        + ":"
        + hl7_DTM[12:14]
        + "Z"
    )


def to_fhir_admission_method(hl7_CWE: str) -> str:
    return ADMISSION_METHOD_MAP[hl7_CWE]


def to_fhir_encounter_class(hl7_CWE: str) -> str:
    return ENCOUNTER_CLASS_MAP[hl7_CWE]
