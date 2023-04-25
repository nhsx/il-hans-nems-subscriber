from typing import Optional


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
