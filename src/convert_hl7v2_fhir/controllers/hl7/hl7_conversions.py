from datetime import datetime

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


def to_fhir_date(hl7_date: str) -> str:
    return str(datetime.strptime(hl7_date[:8], "%Y%m%d").date())


def to_fhir_datetime(hl7_datetime: str) -> str:
    if len(hl7_datetime) != 14:
        raise ValueError(
            "Expected HL7v2 DTM (with time) of length 14 but received length "
            + str(len(hl7_datetime))
            + " instead"
        )

    return datetime.strptime(hl7_datetime, "%Y%m%d%H%M%S").strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def to_fhir_admission_method(hl7_cwe: str) -> str:
    return ADMISSION_METHOD_MAP[hl7_cwe]


def to_fhir_encounter_class(hl7_cwe: str) -> str:
    return ENCOUNTER_CLASS_MAP[hl7_cwe]
