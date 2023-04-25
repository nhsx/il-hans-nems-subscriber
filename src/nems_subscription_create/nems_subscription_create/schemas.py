from fhir.resources.patient import Patient
from pydantic import root_validator


class HANSPatient(Patient):
    """https://simplifier.net/Hospital-Activity-Notification-Service/api-call-example-patient/~json"""

    @root_validator(pre=True)
    def validate_nhs_number_coding(cls, values):
        value_codeable_concept = values["identifier"][0]["extension"][0][
            "valueCodeableConcept"
        ]
        assert (
            value_codeable_concept["coding"][0]["display"] == "Trace required"
        ), "NHS number coding must be: 03 - Trace required"
        assert (
            value_codeable_concept["coding"][0]["code"] == "03"
        ), "NHS number coding must be: 03 - Trace required"
        return values
