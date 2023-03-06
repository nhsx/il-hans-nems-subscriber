from datetime import date
from typing import Optional, Sequence, Tuple

from controllers.exceptions import (
    NameMissmatchError,
    BirthDateMissmatchError,
    NotOKResponseFromPDSError,
)
from external_integrations.pds.api_client import PDSApiClient
from external_integrations.pds.exceptions import InvalidResponseError


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
        # TODO: Prevent timing-based attacks
        try:
            patient_details = self.pds_api_client.get_patient_details(nhs_number)
        except InvalidResponseError:
            raise NotOKResponseFromPDSError

        if not birth_date == patient_details.birthDate:
            raise BirthDateMissmatchError

        if not self._do_names_match(
                family_names=(
                        family_name,
                        patient_details.name[0].family,
                ),  # FIXME: Do not just check 0th element
                given_names=(
                        given_name,
                        patient_details.name[0].given,
                ),  # FIXME: Do not just check 0th element
        ):
            raise NameMissmatchError

    @staticmethod
    def _do_names_match(
            family_names: Tuple[str, str], given_names: Tuple[Sequence[str], Sequence[str]]
    ) -> bool:
        if family_names[0].lower() != family_names[1].lower():
            return False

        if set(n.lower() for n in given_names[0]) != set(
                n.lower() for n in given_names[1]
        ):
            return False

        return True
