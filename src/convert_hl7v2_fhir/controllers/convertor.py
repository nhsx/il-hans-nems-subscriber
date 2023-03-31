from fhir.resources.bundle import Bundle
from hl7 import parse
from jinja2 import Environment, PackageLoader, select_autoescape
from uuid import uuid4

from controllers.hl7utils import get_nhs_number, get_str
from controllers.hl7conversions import to_fhir_date, to_fhir_datetime, to_fhir_admission_method, to_fhir_encounter_class

test_msg_1 = "MSH|^~\&|ADT1|GOOD HEALTH HOSPITAL|GHH LAB, INC.|GOOD HEALTH HOSPITAL|198808181126|SECURITY|ADT^A01^ADT_A01|MSG00001|P|2.8||\rEVN|A01|200708181123||\rPID|1||PATID1234^5^M11^ADT1^MR^GOOD HEALTH HOSPITAL~123456789^^^USSSA^SS||EVERYMAN^ADAM^A^III||19610615|M||C|2222 HOME STREET^^GREENSBORO^NC^27401-1020|GL|(555) 555-2004|(555)555-2004||S||PATID12345001^2^M10^ADT1^AN^A|444333333|987654^NC|\rNK1|1|NUCLEAR^NELDA^W|SPO^SPOUSE||||NK^NEXT OF KIN\rPV1|1|I|2000^2012^01||||004777^ATTEND^AARON^A|||SUR||||ADM|A0|"
test_msg_2 = "MSH|^~\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN~2478684691^^^NHSNBR^NHSNMBR||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^MainBuilding^5|28b|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|||MED|||||||||6145914547062969032^^^^visitid||||||||||||||||||||||ARRIVED|||20200508130643||"
test_msg_3 = "MSH|^~\&|SIMHOSP|SFAC|RAPP|RFAC|20200508130643||ADT^A01|5|T|2.3|||AL||44|ASCII\rEVN|A01|20200508130643|||C006^Wolf^Kathy^^^Dr^^^DRNBR^PRSNL^^^ORGDR|\rPID|1|2590157853^^^SIMULATOR MRN^MRN|2590157853^^^SIMULATOR MRN^MRN||Esterkin^AKI Scenario 6^^^Miss^^CURRENT||19890118000000|F|||170 Juice Place^^London^^RW21 6KC^GBR^HOME||020 5368 1665^HOME|||||||||R^Other - Chinese^^^||||||||\rPD1|||FAMILY PRACTICE^^12345|\rPV1|1|I|RenalWard^MainRoom^Bed 1^Simulated Hospital^^BED^Main" 

class HL7v2ConversionController:
    
    def convert(self, v2msg: str) -> Bundle:
        env = Environment(
            loader=PackageLoader("templates",""),
            autoescape=select_autoescape(["json"])
        )

        env.filters['convert_date'] = to_fhir_date
        env.filters['convert_datetime'] = to_fhir_datetime
        env.filters['map_admissionmethod'] = to_fhir_admission_method
        env.filters['map_encounterclass'] = to_fhir_encounter_class

        template = env.get_template("admit-bundle.json")

        # hopefully we'll be able to fill out the extra info
        #  based on which IP we receive the message from (and can
        #  perform a mapping from IP to below object)
        metadata = {
            "organization": {
                "identifier" : {
                    "value": "XXX"
                },
                "name": "SIMULATED HOSPITAL NHS FOUNDATION TRUST"
            },
            "location": {
                "identifier" : {
                    "value": "XXXY1"
                },
                "address": {
                    "postalCode": "XX20 5XX",
                    "city": "Exampletown"
                }
            }
        }

        # generate a set of UUIDs for each resource in the Bundle
        uuids = {
            "messageHeader" : uuid4(),
            "patient": uuid4(),
            "location": uuid4(),
            "organization" : uuid4(),
            "encounter": uuid4()
        }

        final = template.render(
            msg=parse(v2msg), 
            uuid_method=uuid4, 
            get=get_str, 
            get_nhs_number=get_nhs_number,
            meta=metadata,
            uuids=uuids,
            print=print
            )

        # Check validity by attempting parse
        b = Bundle.parse_raw(str(final))

        return final
    

control = HL7v2ConversionController()
print(control.convert(test_msg_2))
