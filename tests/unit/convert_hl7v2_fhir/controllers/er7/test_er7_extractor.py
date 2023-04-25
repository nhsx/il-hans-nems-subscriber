import pytest

from convert_hl7v2_fhir.controllers.er7.er7_extractor import ER7Extractor
from hl7apy.parser import parse_message

from convert_hl7v2_fhir.controllers.er7.exceptions import (
    InvalidNHSNumberError,
    MissingNHSNumberError,
    ER7ExtractorError,
    MissingPatientClassError,
    MissingAdmissionTypeError,
    MissingTimeOfAdmissionError,
    MissingFamilyNameError,
    MissingGivenNameError,
)

RAW_ER7_MESSAGE_GOOD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_ER7_MESSAGE_INVALID_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~247868469^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_ER7_MESSAGE_MISSING_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_ER7_MESSAGE_MISSING_SEGMENT = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|"
RAW_ER7_MESSAGE_MISSING_FIELD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"


def test_er7_extractor__good_message():
    extractor = ER7Extractor(er7_message=parse_message(RAW_ER7_MESSAGE_GOOD))

    assert extractor.nhs_number() == "2478684691"
    assert extractor.family_name() == "Esterkin"
    assert extractor.given_name() == ["AKI Scenario 6"]
    dob = extractor.date_of_birth()
    assert dob.year == 1989
    assert dob.month == 1
    assert dob.day == 18
    assert extractor.event_type_code() == "A01"
    assert extractor.patient_location() == "RenalWard, Simulated Hospital"
    assert extractor.patient_class() == "I"
    assert extractor.admission_type() == "28b"
    toa = extractor.time_of_admission()
    assert toa.year == 2020
    assert toa.month == 5
    assert toa.day == 8
    assert toa.hour == 13


def test_er7_extractor__invalid_nhs_number():
    extractor = ER7Extractor(
        er7_message=parse_message(RAW_ER7_MESSAGE_INVALID_NHS_NUMBER)
    )

    with pytest.raises(InvalidNHSNumberError):
        extractor.nhs_number()


def test_er7_extractor__missing_nhs_number():
    extractor = ER7Extractor(
        er7_message=parse_message(RAW_ER7_MESSAGE_MISSING_NHS_NUMBER)
    )

    with pytest.raises(MissingNHSNumberError):
        extractor.nhs_number()


def test_er7_extractor__missing_segment():
    extractor = ER7Extractor(er7_message=parse_message(RAW_ER7_MESSAGE_MISSING_SEGMENT))

    with pytest.raises(ER7ExtractorError):
        extractor.patient_location()

    with pytest.raises(MissingPatientClassError):
        extractor.patient_class()

    with pytest.raises(MissingAdmissionTypeError):
        extractor.admission_type()

    with pytest.raises(MissingTimeOfAdmissionError):
        extractor.time_of_admission()


def test_er7_extractor__missing_field():
    extractor = ER7Extractor(er7_message=parse_message(RAW_ER7_MESSAGE_MISSING_FIELD))

    with pytest.raises(MissingFamilyNameError):
        extractor.family_name()

    with pytest.raises(MissingGivenNameError):
        extractor.given_name()
