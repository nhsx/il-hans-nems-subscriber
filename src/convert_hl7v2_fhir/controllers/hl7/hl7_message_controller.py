import re
from typing import Any, Dict, Optional
from uuid import uuid4, UUID

from fhir.resources.bundle import Bundle
from hl7 import Message

from controllers.hl7.exceptions import (
    MissingSegmentError,
    MissingFieldOrComponentError,
    MissingNHSNumberError,
    InvalidNHSNumberError,
)
from controllers.hl7.hl7_conversions import (
    to_fhir_date,
    to_fhir_datetime,
    to_fhir_admission_method,
    to_fhir_encounter_class,
)
from controllers.utils import is_nhs_number_valid


class HL7MessageController:
    def __init__(
        self,
        hl7_message: Message,
        message_header_uuid: Optional[UUID] = None,
        organization_uuid: Optional[UUID] = None,
        encounter_uuid: Optional[UUID] = None,
        patient_uuid: Optional[UUID] = None,
        location_uuid: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.hl7_message = hl7_message
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

    def _extract_field(self, segment_name: str, *indexes: int) -> str:
        try:
            _field = self.hl7_message[segment_name]
            for index in indexes:
                _field = _field[index]
        except KeyError:
            raise MissingSegmentError(f"Required segment '{segment_name}' was missing.")
        except IndexError:
            field_indexes = ".".join(str(i) for i in indexes)
            raise MissingFieldOrComponentError(
                f"Required field '{segment_name}.{field_indexes}' was missing."
            )
        return str(_field)

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
                    "code": self._extract_field("EVN", 0, 1),
                },
                "source": {"endpoint": "http://example.com/fhir/R4"},
                "responsible": {"reference": f"urn:uuid:{self.organization_uuid}"},
                "focus": [{"reference": f"urn:uuid:{self.encounter_uuid}"}],
            },
        }

    def _create_patient(self) -> Dict[str, Any]:
        nhs_number = self._extract_nhs_number()
        family_name = self._extract_field("PID", 0, 5, 0, 0)
        given_name = [
            name
            for name in (
                self._extract_field("PID", 0, 5, 0, 1),
                self._extract_field("PID", 0, 5, 0, 2),
            )
            if name
        ]
        birth_date = to_fhir_date(self._extract_field("PID", 0, 7))

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
                        "value": nhs_number,
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
                "name": [{"use": "usual", "family": family_name, "given": given_name}],
                "birthDate": birth_date,
            },
        }

    def _create_location(self):
        location_name = [
            name
            for name in (
                self._extract_field("PV1", 0, 3, 0, 0),
                self._extract_field("PV1", 0, 3, 0, 3),
            )
            if name
        ]
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
                "name": ", ".join(location_name),
                "address": {
                    "line": location_name,
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
        resource_class = to_fhir_encounter_class(self._extract_field("PV1", 0, 2))
        resource_period_start = to_fhir_datetime(self._extract_field("PV1", 0, 44))
        admission_method_coding = to_fhir_admission_method(
            self._extract_field("PV1", 0, 4)
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
                "period": {"start": resource_period_start},
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

    def _extract_nhs_number(self):
        pid_segment = self._extract_field("PID")
        potential_nhs_numbers = set(re.findall(r"\d{10}", pid_segment))
        if "NHSNMBR" not in pid_segment or not potential_nhs_numbers:
            raise MissingNHSNumberError

        try:
            return next(
                (
                    potential_nhs_number
                    for potential_nhs_number in potential_nhs_numbers
                    if is_nhs_number_valid(potential_nhs_number)
                )
            )
        except StopIteration:
            raise InvalidNHSNumberError
