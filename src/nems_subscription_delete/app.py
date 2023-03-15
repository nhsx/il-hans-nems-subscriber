from uuid import UUID

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext
from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue

_LOGGER = Logger()


@_LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    try:
        UUID(event["pathParameters"]["id"])
    except ValueError:
        return {
            "statusCode": 500,
            "body": OperationOutcome(
                issue=[
                    OperationOutcomeIssue(
                        severity="error",
                        code="exception",
                        diagnostics="subscription_id is not a valid UUID",
                    )
                ]
            ).json(),
        }
    return {"statusCode": 200}
