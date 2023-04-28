from typing import Dict
from unittest.mock import MagicMock

import hl7
import pytest
from pytest_mock import MockFixture

from convert_hl7v2_fhir import app
from convert_hl7v2_fhir.app import lambda_handler
from convert_hl7v2_fhir.controllers.hl7.hl7_ack_builder import HL7ErrorCode

RAW_HL7_MESSAGE_GOOD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_NOT_INPATIENT_CLASS = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|E|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_INVALID_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~247868469^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_NHS_NUMBER = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_SEGMENT = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|"
RAW_HL7_MESSAGE_MISSING_FIELD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_HOSPITAL_AND_WARD = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|9728002378^^^NHSNBR^NHSNMBR|9728002378^^^NHSNBR^NHSNMBR||PUCKEY^Miles^Keith^^^^CURRENT||19610608000000|M||||||||||||||||||||||\rPV1|1|I|^MainRoom^Bed 1^^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_ADMISSION_TIME = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|9728002378^^^NHSNBR^NHSNMBR|9728002378^^^NHSNBR^NHSNMBR||PUCKEY^Miles^Keith^^^^CURRENT||19610608000000|M||||||||||||||||||||||\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||||"
RAW_HL7_MESSAGE_MISSING_FAMILY_NAME = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1||9728002378^^^NHSNBR^NHSNMBR||^Miles^Keith^^^^CURRENT||19610608000000|M||||||||||||||||||||||\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_MISSING_DATE_OF_BIRTH = "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20230411130643|||C006^Buckley^Mark^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1||9728002378^^^NHSNBR^NHSNMBR||PUCKEY^Miles^Keith^^^^CURRENT|||M||||||||||||||||||||||\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main Building^5|28b||||||MED|||||||||||||||||||||||||||||||ARRIVED|||20200508130643||"
RAW_HL7_MESSAGE_NOT_ADT_TYPE = """MSH|^~\\&|SendingApp|SendingFac|ReceivingApp|ReceivingFac|20120411070545||ORU^R01|59689|P|2.3\rPID|1|12345|12345^^^MIE&1.2.840.114398.1.100&ISO^MR||MOUSE^MINNIE^S||19240101|F|||123 MOUSEHOLE LN^^FORT WAYNE^IN^46808|||||||||||||||||||\rPV1|1|O|||||71^DUCK^DONALD||||||||||||12376|||||||||||||||||||||||||20120410160227||||||\rORC|RE||12376|||||||100^DUCK^DASIY||71^DUCK^DONALD|^^^||20120411070545|||||\rOBR|1||12376|cbc^CBC|R||20120410160227|||22^GOOF^GOOFY|||Fasting: No|201204101625||71^DUCK^DONALD||||||201204101630|||F||^^^^^R|||||||||||||||||85025|\rOBX|1|NM|wbc^Wbc^Local^6690-2^Wbc^LN||7.0|/nl|3.8-11.0||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|2|NM|neutros^Neutros^Local^770-8^Neutros^LN||68|%|40-82||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|3|NM|lymphs^Lymphs^Local^736-9^Lymphs^LN||20|%|11-47||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|4|NM|monos^Monos^Local^5905-5^Monos^LN||16|%|4-15|H|||F|||20120410160227|lab|12^XYZ LAB|\rOBX|5|NM|eo^Eos^Local^713-8^Eos^LN||3|%|0-8||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|6|NM|baso^Baso^Local^706-2^Baso^LN||0|%|0-1||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|7|NM|ig^Imm Gran^Local^38518-7^Imm Gran^LN||0|%|0-2||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|8|NM|rbc^Rbc^Local^789-8^Rbc^LN||4.02|/pl|4.07-4.92|L|||F|||20120410160227|lab|12^XYZ LAB|\rOBX|9|NM|hgb^Hgb^Local^718-7^Hgb^LN||13.7|g/dl|12.0-14.1||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|10|NM|hct^Hct^Local^4544-3^Hct^LN||40|%|34-43||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|11|NM|mcv^Mcv^Local^787-2^Mcv^LN||80|fl|77-98||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|12|NM|mch^Mch||30|pg|27-35||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|13|NM|mchc^Mchc||32|g/dl|32-35||||F|||20120410160227|lab|12^XYZ LAB|\rOBX|14|NM|plt^Platelets||221|/nl|140-400||||F|||20120410160227|lab|12^XYZ LAB|"""
RAW_HL7_MESSAGE_NOT_A01_TRIGGER = """MSH|^~\\&|SendingApp|SendingFacility|HL7API|PKB|20160102101112||ADT^A03|ABC0000000001|P|2.4\rPID|||9999999999^^^NHS^NH||Smith^John^Joe^^Mr||19700101|M|||Flat name^1, The Road^London^London^SW1A 1AA^GBR||01234567890^PRN~07123456789^PRS|^NET^^john.smith@company.com~01234098765^WPN||||||||||||||||N|\rPV1|1|I|^^^^^^^^My Ward||||^Jones^Stuart^James^^Dr^|^Smith^William^^^Dr^|^Foster^Terry^^^Mr^||||||||||V00001|||||||||||||||||||||||||201508011000|201508011200"""

_DUMMY_LAMBDA_CONTEXT = MagicMock(
    function_name="test",
    function_memory_size="test",
    function_arn="test",
    function_request_id="test",
)


@pytest.fixture()
def mock_is_patient_added_to_hans(mocker: MockFixture) -> None:
    mocker.patch.object(
        app, app._is_patient_added_to_hans.__name__, MagicMock(return_value=True)
    )


@pytest.fixture()
def mock_send_to_sqs(mocker: MockFixture) -> None:
    mocker.patch.object(app, app._send_to_sqs.__name__)


def _create_lambda_body(hl7_raw_message: str) -> Dict[str, str]:
    return {"body": hl7_raw_message}


def test_lambda_handler__message_body_contains_ack(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    event = _create_lambda_body(RAW_HL7_MESSAGE_GOOD)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSH"]
    assert message["MSA"]


def test_lambda_handler__ack_correct_recipient(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # when
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_GOOD), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSH"][0][5][0] == "SIMHOSP"
    assert message["MSH"][0][6][0] == "SFAC"


def test_lambda_handler__good_message_correct_accept_code(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # when
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_GOOD), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AA"


def test_lambda_handler__correct_accept_code_for_invalid_nhs_number(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_INVALID_NHS_NUMBER), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "102"


def test_lambda_handler__correct_accept_code_for_missing_nhs_number(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    response = lambda_handler(
        _create_lambda_body(RAW_HL7_MESSAGE_MISSING_NHS_NUMBER), _DUMMY_LAMBDA_CONTEXT
    )
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "204"


def test_lambda_handler__missing_segment(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_SEGMENT)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == "100"


def test_lambda_handler__missing_hospital_and_ward(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_HOSPITAL_AND_WARD)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])


def test_lambda_handler__missing_admission_time(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_ADMISSION_TIME)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])
    assert "PV1_44" in str(message["ERR"][0])


def test_lambda_handler__missing_family_name(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_FAMILY_NAME)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])
    assert "PID_5" in str(message["ERR"][0])


def test_lambda_handler__missing_date_of_birth(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_MISSING_DATE_OF_BIRTH)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.REQUIRED_FIELD_MISSING.value)
    assert "Required field was missing" in str(message["ERR"][0])
    assert "PID_7" in str(message["ERR"][0])


def test_lambda_handler__unsupported_message_type(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_NOT_ADT_TYPE)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.UNSUPPORTED_MESSAGE_TYPE.value)


def test_lambda_handler__unsupported_event_code(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_NOT_A01_TRIGGER)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
    assert message["ERR"][0][3][0] == str(HL7ErrorCode.UNSUPPORTED_EVENT_CODE.value)


def test_lambda_handler__unsupported_patient_class(
    mock_is_patient_added_to_hans: None, mock_send_to_sqs: None
):
    # given
    event = _create_lambda_body(RAW_HL7_MESSAGE_NOT_INPATIENT_CLASS)

    # when
    response = lambda_handler(event, _DUMMY_LAMBDA_CONTEXT)
    message = hl7.parse(response["body"])

    # then
    assert message["MSA"][0][1][0] == "AR"
