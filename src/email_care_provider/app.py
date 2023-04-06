from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from controllers.notify_care_provider import NotifyCareProviderController
from schemas import HANSBundle

_LOGGER = Logger()


@_LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    for queue_message in event:
        bundle = HANSBundle.parse_raw(queue_message["body"])
        NotifyCareProviderController().send_email_to_care_provider(
            patient_nhs_number=bundle.patient.identifier[0].value,
            patient_given_name=bundle.patient.name[0].given[0],
            patient_family_name=bundle.patient.name[0].family,
            patient_birth_date=bundle.patient.birthDate,
            location_name=bundle.location.name,
            admitted_at=bundle.encounter.period.start,
        )
