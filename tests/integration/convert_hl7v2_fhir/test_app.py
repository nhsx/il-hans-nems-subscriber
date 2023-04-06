import pytest

from aws_lambda_powertools.utilities.typing import LambdaContext
from hl7 import parse

from app import lambda_handler, _send_to_sqs

msg_known_good = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"

msg_invalid_nhs_no = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~247868469^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
msg_missing_nhs_no = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
msg_missing_segment = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|"
msg_missing_field = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"


def _create_dummy_context() -> dict:
    return {
        "function_name": "test",
        "function_memory_size": "test",
        "function_arn": "test",
        "function_request_id": "test",
    }


def _create_lambda_body(v2msg: str) -> dict:
    return {"body": v2msg}


def test_lambda_handler__ACK_message_in_body(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    resp = lambda_handler(_create_lambda_body(msg_known_good), _create_dummy_context())
    msg = parse(resp["body"])
    # test
    assert msg["MSH"]
    assert msg["MSA"]


def test_lambda_handler__ACK_correct_recipient(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    resp = lambda_handler(_create_lambda_body(msg_known_good), _create_dummy_context())
    msg = parse(resp["body"])
    # test
    assert msg["MSH"][0][5][0] == "SIMHOSP"
    assert msg["MSH"][0][6][0] == "SFAC"


def test_lambda_handler__good_message_AA(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    resp = lambda_handler(_create_lambda_body(msg_known_good), _create_dummy_context())
    msg = parse(resp["body"])
    # test
    assert msg["MSA"][0][1][0] == "AA"


def test_lambda_handler__invalid_nhs_num_AR(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    resp = lambda_handler(
        _create_lambda_body(msg_invalid_nhs_no), _create_dummy_context()
    )
    msg = parse(resp["body"])
    # test
    assert msg["MSA"][0][1][0] == "AR"
    assert msg["ERR"][0][3][0] == "102"


def test_lambda_handler__missing_nhs_num_AR(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    resp = lambda_handler(
        _create_lambda_body(msg_missing_nhs_no), _create_dummy_context()
    )
    msg = parse(resp["body"])
    # test
    assert msg["MSA"][0][1][0] == "AR"
    assert msg["ERR"][0][3][0] == "204"


def test_lambda_handler__missing_segment(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    resp = lambda_handler(
        _create_lambda_body(msg_missing_segment), _create_dummy_context()
    )
    msg = parse(resp["body"])
    # test
    assert msg["MSA"][0][1][0] == "AR"
    assert msg["ERR"][0][3][0] == "100"


def test_lambda_handler__missing_field(mocker):
    mocker.patch("app._send_to_sqs")
    # given
    resp = lambda_handler(
        _create_lambda_body(msg_missing_field), _create_dummy_context()
    )
    msg = parse(resp["body"])
    # test
    assert msg["MSA"][0][1][0] == "AR"
    assert msg["ERR"][0][3][0] == "101"
