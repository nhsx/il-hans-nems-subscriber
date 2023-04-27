from typing import Dict

import hl7
from convert_hl7v2_fhir.app import lambda_handler
from convert_hl7v2_fhir.controllers.hl7.hl7_ack_builder import HL7ErrorCode

RAW_HL7_MESSAGE_GOOD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_INVALID_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~247868469^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_SEGMENT = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|"
RAW_HL7_MESSAGE_MISSING_FIELD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_HOSPITAL_AND_WARD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|9728002378^^^NHSNBR^NHSNMBR|9728002378^^^NHSNBR^NHSNMBR||PUCKEY^Miles^Keith^^^^CURRENT||19610608000000|M||||||||||||||||||||||\rPV1|1|I|^MainRoom^Bed 1^^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_ADMISSION_TIME = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|9728002378^^^NHSNBR^NHSNMBR|9728002378^^^NHSNBR^NHSNMBR||PUCKEY^Miles^Keith^^^^CURRENT||19610608000000|M||||||||||||||||||||||\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||||"
RAW_HL7_MESSAGE_MISSING_FAMILY_NAME = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1||9728002378^^^NHSNBR^NHSNMBR||^Miles^Keith^^^^CURRENT||19610608000000|M||||||||||||||||||||||\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_DATE_OF_BIRTH = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1||9728002378^^^NHSNBR^NHSNMBR||PUCKEY^Miles^Keith^^^^CURRENT|||M||||||||||||||||||||||\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||20200508130643||"

_DUMMY_LAMBDA_CONTEXT = {
    "function_name": "test",
    "function_memory_size": "test",
    "function_arn": "test",
    "function_request_id": "test",
}


def _create_lambda_body(hl7_raw_message: str) -> Dict[str, str]:
    return {"body": hl7_raw_message}


def test_lambda_handler__message_body_contains_ack(mocker):
    # given
    _send_to_sqs_mocked = mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_GOOD)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSH"]
    assert message["MSA"]


def test_lambda_handler__ack_correct_recipient(mocker):
    # given
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")

    # when
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_GOOD), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSH"][0][5][0] == "SIMHOSP"
    assert message["MSH"][0][6][0] == "SFAC"


def test_lambda_handler__good_message_correct_accept_code(mocker):
    # given
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")

    # when
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_GOOD), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AA"


def test_lambda_handler__correct_accept_code_for_invalid_nhs_number(mocker):
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    # given
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_INVALID_NHS_NUMBER), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "102"


def test_lambda_handler__correct_accept_code_for_missing_nhs_number(mocker):
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    # given
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_MISSING_NHS_NUMBER), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "204"


def test_lambda_handler__missing_segment(mocker):
    # given
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_SEGMENT)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "100"


def test_lambda_handler__missing_hospital_and_ward(mocker):
    # given
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_HOSPITAL_AND_WARD)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])


def test_lambda_handler__missing_admission_time(mocker):
    # given
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_ADMISSION_TIME)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])
    assert "PV1_44" in str(message["ERR"][0])


def test_lambda_handler__missing_family_name(mocker):
    # given
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_FAMILY_NAME)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])
    assert "PID_5" in str(message["ERR"][0])


def test_lambda_handler__missing_date_of_birth(mocker):
    # given
    mocker.patch("convert_hl7v2_fhir.app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_DATE_OF_BIRTH)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])
    assert "PID_7" in str(message["ERR"][0])
