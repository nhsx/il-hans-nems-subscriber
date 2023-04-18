from hl7 import parse
from convert_hl7v2_fhir import app
from convert_hl7v2_fhir.app import lambda_handler

RAW_HL7_MESSAGE_GOOD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_INVALID_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~247868469^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_SEGMENT = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|"
RAW_HL7_MESSAGE_MISSING_FIELD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"

_DUMMY_LAMBDA_CONTEXT = {
    "function_name": "test",
    "function_memory_size": "test",
    "function_arn": "test",
    "function_request_id": "test",
}


def _create_lambda_body(hl7_raw_message: str) -> Dict[str, str]:
    return {"body": hl7_raw_message}


def _create_lambda_body(v2msg: str) -> dict:
    return {"body": v2msg}


def test_lambda_handler__ACK_message_in_body(mocker):
    mocker.patch.object(app, app._send_to_sqs.__name__)
    # given
    _send_to_sqs_mocked = mocker.patch("app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_GOOD)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSH"]
    assert message["MSA"]


def test_lambda_handler__ACK_correct_recipient(mocker):
    mocker.patch.object(app, app._send_to_sqs.__name__)
    # given
    resp = lambda_handler(_create_lambda_body(msg_known_good), _create_dummy_context())
    msg = parse(resp["body"])
    # test
    assert msg["MSH"][0][5][0] == "SIMHOSP"
    assert msg["MSH"][0][6][0] == "SFAC"


def test_lambda_handler__good_message_AA(mocker):
    mocker.patch.object(app, app._send_to_sqs.__name__)
    # given
    resp = lambda_handler(_create_lambda_body(msg_known_good), _create_dummy_context())
    msg = parse(resp["body"])
    # test
    assert msg["MSA"][0][1][0] == "AA"


def test_lambda_handler__invalid_nhs_num_AR(mocker):
    mocker.patch.object(app, app._send_to_sqs.__name__)
    # given
    resp = lambda_handler(
        _create_lambda_body(msg_invalid_nhs_no), _create_dummy_context()
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSH"][0][5][0] == "SIMHOSP"
    assert message["MSH"][0][6][0] == "SFAC"


def test_lambda_handler__missing_nhs_num_AR(mocker):
    mocker.patch.object(app, app._send_to_sqs.__name__)
    # given
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_INVALID_NHS_NUMBER), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "102"


def test_lambda_handler__correct_accept_code_for_missing_nhs_number(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_MISSING_NHS_NUMBER), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "204"


def test_lambda_handler__missing_segment(mocker):
    mocker.patch.object(app, app._send_to_sqs.__name__)
    # given
    mocker.patch("app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_SEGMENT)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "100"


def test_lambda_handler__missing_field(mocker):
    mocker.patch.object(app, app._send_to_sqs.__name__)
    # given
    mocker.patch("app._send_to_sqs")
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_FIELD)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "101"
