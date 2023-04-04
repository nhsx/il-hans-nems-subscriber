from boto3 import client
import hl7
import json

from controllers.hl7builder import generate_ACK_message
from controllers.convertor import HL7v2ConversionController
from internal_integrations.sqs.settings import SQSSettings

def lambda_handler(event, context):
    body = str(event["body"])

    # hl7 messages expect \r rather than \r\n (and the parsing library)
    #  will reject otherwise (with a KeyError)
    msg_parsed = hl7.parse(body.replace("\n", ""))

    fhir_json = convert(msg_parsed)

    sqs = client('sqs')
    sqs_settings = SQSSettings()

    sqs.send_message(
        QueueUrl=sqs_settings.converted_queue_url,
        MessageBody=fhir_json
    )

    return {
        "statusCode": 200,
        "headers": {
            "content-type": "x-application/hl7-v2+er; charset=utf-8"
        },
        "body": create_ack(msg_parsed)
    }
    

def create_ack(msg_parsed: hl7.Message):
    sending_app = msg_parsed["MSH"][0][3][0]
    sending_facility = msg_parsed["MSH"][0][4][0]
    msg_control_id = msg_parsed["MSH"][0][10][0]
    return generate_ACK_message(
        recipient_app=sending_app,
        recipient_facility=sending_facility,
        replying_to_msgid=msg_control_id
    )


def convert(v2msg : str) -> str:
    convertor = HL7v2ConversionController()
    return convertor.convert(v2msg)

#print(lambda_handler({
#    "body": "MSH|^~\\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
#},{}))