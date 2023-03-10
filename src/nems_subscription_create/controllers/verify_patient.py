from datetime import date
from typing import Optional, Sequence, Tuple

from fhir.resources.humanname import HumanName

from controllers.exceptions import (
    NameMissmatch,
    BirthDateMissmatch,
    IncorrectNHSNumber,
    PatientNotFound,
    InternalError,
)
from external_integrations.pds.api_client import PDSApiClient
from external_integrations.pds.exceptions import (
    InvalidNHSNumber,
    MissingNHSNumber,
    PatientDoesNotExist,
    PatientDidButNoLongerExists,
    UnknownPDSError,
    PDSUnavailable,
)


class VerifyPatientController:
    def __init__(self, pds_api_client: Optional[PDSApiClient] = None):
        self.pds_api_client: PDSApiClient = pds_api_client or PDSApiClient()

    def verify_patient_data(
        self, *, nhs_number: str, patient_name: HumanName, birth_date: date
    ) -> None:
        # TODO: Prevent timing-based attacks
        try:
            patient_details = self.pds_api_client.get_patient_details(nhs_number)
        except (InvalidNHSNumber, MissingNHSNumber):
            raise IncorrectNHSNumber
        except (PatientDoesNotExist, PatientDidButNoLongerExists):
            raise PatientNotFound
        except (UnknownPDSError, PDSUnavailable):
            raise InternalError

        if not birth_date == patient_details.birthDate:
            raise BirthDateMissmatch

        if not any(
            self._do_human_names_match(patient_name, pds_name)
            for pds_name in patient_details.name
        ):
            raise NameMissmatch

    @staticmethod
    def _do_human_names_match(human_name_1: HumanName, human_name_2: HumanName) -> bool:
        if human_name_1.family.lower() != human_name_2.family.lower():
            return False

        if human_name_1.given[0].lower() != human_name_2.given[0].lower():
            return False

        return True
