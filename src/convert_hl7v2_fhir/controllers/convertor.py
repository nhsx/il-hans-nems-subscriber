from fhir.resources.bundle import Bundle
from hl7 import Message
from jinja2 import Environment, PackageLoader, select_autoescape
from uuid import uuid4

from controllers.hl7utils import get_nhs_number, get_str
from controllers.hl7conversions import to_fhir_date, to_fhir_datetime, to_fhir_admission_method, to_fhir_encounter_class

class HL7v2ConversionController:
    
    def convert(self, v2msg_parsed: Message) -> Bundle:
        env = Environment(
            loader=PackageLoader("controllers.templates",""),
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
            msg=v2msg_parsed, 
            uuid_method=uuid4, 
            get=get_str, 
            get_nhs_number=get_nhs_number,
            meta=metadata,
            uuids=uuids,
            print=print
            )

        # check validity by attempting parse
        Bundle.parse_raw(str(final))

        return final
