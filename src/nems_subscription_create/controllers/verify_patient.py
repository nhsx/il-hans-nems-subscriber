from datetime import date
from typing import Optional, Sequence, Tuple

from exceptions import NameMissmatch, BirthDateMissmatch
from src.nems_subscription_create.external_integrations.pds.api_client import (
    PDSApiClient,
)


class VerifyPatientController:
    def __init__(self, pds_api_client: Optional[PDSApiClient] = None):
        self.pds_api_client: PDSApiClient = pds_api_client or PDSApiClient()

    def verify_patient_data(
        self,
        *,
        nhs_number: str,
        family_name: str,
        given_name: Sequence[str],
        birth_date: date
    ) -> None:
        patient_details = self.pds_api_client.get_patient_details(nhs_number)
        if not self._do_names_match(
            family_names=(family_name, patient_details.name.family),
            given_names=(given_name, patient_details.name.given),
        ):
            raise NameMissmatch

        if not birth_date == patient_details.birthDate:
            raise BirthDateMissmatch

    @staticmethod
    def _do_names_match(
        family_names: Tuple[str, str], given_names: Tuple[Sequence[str], Sequence[str]]
    ) -> bool:
        if family_names[0].lower() != family_names[1].lower():
            return False

        if not any(
            given_name.lower() in set(n.lower() for n in given_names[1])
            for given_name in given_names[0]
        ):
            return False

        return True
