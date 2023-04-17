from datetime import datetime, date
from typing import Optional

from notifications_python_client.notifications import NotificationsAPIClient

from email_care_provider.external_integrations.notify.settings import (
    get_notify_settings,
)
from email_care_provider.internal_integrations.management_interface.api_client import (
    ManagementInterfaceApiClient,
)
from hashlib import scrypt


class NotifyCareProviderController:
    def __init__(
        self,
        notifications_api_client: Optional[NotificationsAPIClient] = None,
        management_interface_api_client: Optional[ManagementInterfaceApiClient] = None,
    ):
        self.notifications_api_client = (
            notifications_api_client
            or NotificationsAPIClient(api_key=get_notify_settings().api_key)
        )
        self.management_interface_api_client = (
            management_interface_api_client or ManagementInterfaceApiClient()
        )

    def send_email_to_care_provider(
        self,
        *,
        patient_nhs_number: str,
        patient_given_name: str,
        patient_family_name: str,
        patient_birth_date: date,
        location_name: str,
        admitted_at: datetime
    ) -> None:
        care_provider_response = self.management_interface_api_client.get_care_provider(
            care_recipient_pseudo_id=self._generate_pseudo_id(
                nhs_number=patient_nhs_number, birth_date=patient_birth_date
            )
        )
        self.notifications_api_client.send_email_notification(
            email_address=care_provider_response.telecom[0].value,
            template_id=get_notify_settings().email_templates.ADMISSION,
            personalisation={
                "subj_given_name": patient_given_name,
                "subj_family_name": patient_family_name,
                "recp_given_name": care_provider_response.name,
                "subj_DOB": str(patient_birth_date),
                "event_loc": location_name,
                "event_time_str": str(admitted_at.time()),
                "event_date_str": str(admitted_at.date()),
            },
        )

    @staticmethod
    def _generate_pseudo_id(nhs_number: str, birth_date: date) -> str:
        # https://nhsx.github.io/il-hans-infrastructure/adrs/003-Do-not-use-NEMS-or-MESH
        return scrypt(
            nhs_number.encode(),
            salt=str(birth_date).encode(),
            n=32768,
            r=12,
            p=6,
            maxmem=2**26,
        ).hex()
