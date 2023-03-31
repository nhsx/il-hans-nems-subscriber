import hl7

from fhir.resources.bundle import Bundle, BundleEntry

import controllers.hl7builder

def lambda_handler(event, context):
    body = event["body"]
    fhir_json = convert(body)
    return {
        "statusCode": 200,
        "body": fhir_json
    }


def convert(v2msg : str):
    m = hl7.parse(v2msg)
    print(type(m))
    return ""
