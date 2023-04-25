from uuid import UUID

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from nems_subscription_delete.utils import operation_outcome_lambda_response_factory

_LOGGER = Logger()


@_LOGGER.inject_lambda_context(log_event=True)
def lambda_handler(event: dict, context: LambdaContext):
    try:
        UUID(event["pathParameters"]["id"])
    except ValueError:
        return operation_outcome_lambda_response_factory(
            status_code=500,
            severity="error",
            code="exception",
            diagnostics="Provided subscription id is not a valid UUID",
        )
    except KeyError:
        return operation_outcome_lambda_response_factory(
            status_code=500,
            severity="error",
            code="exception",
            diagnostics="Missing subscription id in path parameters",
        )

    return {"statusCode": 200}
