from fhir.resources.bundle import Bundle
from fhir.resources.patient import Patient
from fhir.resources.location import Location
from fhir.resources.encounter import Encounter


class HANSBundle(Bundle):
    @property
    def patient(self) -> Patient:
        return self.entry[1].resource

    @property
    def location(self) -> Location:
        return self.entry[2].resource

    @property
    def encounter(self) -> Encounter:
        return self.entry[4].resource
