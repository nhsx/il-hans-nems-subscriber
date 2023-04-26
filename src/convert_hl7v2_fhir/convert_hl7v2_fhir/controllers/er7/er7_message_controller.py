from typing import Any, Dict, Optional
from uuid import uuid4, UUID

from fhir.resources.bundle import Bundle
from hl7apy.core import Message

from convert_hl7v2_fhir.controllers.er7.er7_extractor import ER7Extractor
from convert_hl7v2_fhir.controllers.hl7.hl7_conversions import (
    to_fhir_admission_method,
    to_fhir_encounter_class,
)


class ER7MessageController:
    def __init__(
        self,
        er7_message: Message,
        message_header_uuid: Optional[UUID] = None,
        organization_uuid: Optional[UUID] = None,
        encounter_uuid: Optional[UUID] = None,
        patient_uuid: Optional[UUID] = None,
        location_uuid: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.er7_message = er7_message
        self.extractor = ER7Extractor(er7_message=self.er7_message)
        self.message_header_uuid = message_header_uuid or uuid4()
        self.organization_uuid = organization_uuid or uuid4()
        self.encounter_uuid = encounter_uuid or uuid4()
        self.patient_uuid = patient_uuid or uuid4()
        self.location_uuid = location_uuid or uuid4()
        # hopefully we'll be able to fill out the extra info
        #  based on which IP we receive the message from (and can
        #  perform a mapping from IP to below object)
        self.metadata = metadata or {
            "organization": {
                "identifier": {"value": "XXX"},
                "name": "SIMULATED HOSPITAL NHS FOUNDATION TRUST",
            },
            "location": {
                "identifier": {"value": "XXXY1"},
                "address": {"postalCode": "XX20 5XX", "city": "Exampletown"},
            },
        }

    def to_fhir_bundle(self) -> Bundle:
        bundle_json = {
            "resourceType": "Bundle",
            "type": "message",
            "meta": {
                "profile": [
                    "https://fhir.simplifier.net/Hospital-Activity-Notification-Service/StructureDefinition/ActivityNotification-Bundle"
                ]
            },
            "entry": [
                self._create_header(),
                self._create_patient(),
                self._create_location(),
                self._create_organization(),
                self._create_encounter(),
            ],
        }
        return Bundle(**bundle_json)

    def _create_header(self) -> Dict[str, Any]:
        return {
            "fullUrl": f"urn:uuid:{self.message_header_uuid}",
            "resource": {
                "resourceType": "MessageHeader",
                "id": str(self.message_header_uuid),
                "meta": {
                    "profile": [
                        "https://fhir.simplifier.net/Hospital-Activity-Notification-Service/StructureDefinition/ActivityNotification-UKCore-MessageHeader"
                    ]
                },
                "eventCoding": {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0003",
                    "code": self.extractor.event_type_code(),
                },
                "source": {"endpoint": "http://example.com/fhir/R4"},
                "responsible": {"reference": f"urn:uuid:{self.organization_uuid}"},
                "focus": [{"reference": f"urn:uuid:{self.encounter_uuid}"}],
            },
        }

    def _create_patient(self) -> Dict[str, Any]:
        return {
            "fullUrl": f"urn:uuid:{self.patient_uuid}",
            "resource": {
                "resourceType": "Patient",
                "id": str(self.patient_uuid),
                "meta": {
                    "profile": [
                        "https://fhir.simplifier.net/Hospital-Activity-Notification-Service/StructureDefinition/ActivityNotification-UKCore-Patient"
                    ]
                },
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/nhs-number",
                        "value": self.extractor.nhs_number(),
                        "extension": [
                            {
                                "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                                "valueCodeableConcept": {
                                    "coding": [
                                        {
                                            "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatusEngland",
                                            "code": "01",
                                            "display": "Number present and verified",
                                        }
                                    ]
                                },
                            }
                        ],
                    }
                ],
                "name": [
                    {
                        "use": "usual",
                        "family": self.extractor.family_name(),
                        "given": self.extractor.given_name(),
                    }
                ],
                "birthDate": self.extractor.date_of_birth(),
            },
        }

    def _create_location(self):
        return {
            "fullUrl": f"urn:uuid:{self.location_uuid}",
            "resource": {
                "resourceType": "Location",
                "id": str(self.location_uuid),
                "meta": {
                    "profile": [
                        "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Location"
                    ]
                },
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/ods-site-code",
                        "value": self.metadata["location"]["identifier"]["value"],
                    }
                ],
                "status": "active",
                "name": self.extractor.patient_location(),
                "address": {
                    "line": [
                        l.strip() for l in self.extractor.patient_location().split(",")
                    ],
                    "city": self.metadata["location"]["address"]["city"],
                    "postalCode": self.metadata["location"]["address"]["postalCode"],
                },
            },
        }

    def _create_organization(self):
        return {
            "fullUrl": f"urn:uuid:{self.organization_uuid}",
            "resource": {
                "resourceType": "Organization",
                "id": str(self.organization_uuid),
                "meta": {
                    "profile": [
                        "https://fhir.hl7.org.uk/StructureDefinition/UKCore-Organization"
                    ]
                },
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                        "value": self.metadata["organization"]["identifier"]["value"],
                    }
                ],
                "name": self.metadata["organization"]["name"],
            },
        }

    def _create_encounter(self):
        resource_class = to_fhir_encounter_class(self.extractor.patient_class())
        admission_method_coding = to_fhir_admission_method(
            self.extractor.admission_type()
        )
        return {
            "fullUrl": f"urn:uuid:{self.encounter_uuid}",
            "resource": {
                "resourceType": "Encounter",
                "id": str(self.encounter_uuid),
                "meta": {
                    "profile": [
                        "https://fhir.simplifier.net/Hospital-Activity-Notification-Service/StructureDefinition/ActivityNotification-UKCore-Encounter"
                    ]
                },
                "status": "in-progress",
                "subject": {"reference": f"urn:uuid:{self.patient_uuid}"},
                "class": resource_class,
                "period": {"start": self.extractor.time_of_admission()},
                "location": [
                    {
                        "status": "active",
                        "location": {"reference": f"urn:uuid:{self.location_uuid}"},
                    }
                ],
                "extension": [
                    {
                        "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AdmissionMethod",
                        "valueCodeableConcept": {"coding": [admission_method_coding]},
                    }
                ],
            },
        }
