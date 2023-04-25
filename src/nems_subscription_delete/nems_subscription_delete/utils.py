from typing import Dict, Any

from fhir.resources.operationoutcome import OperationOutcome, OperationOutcomeIssue


def operation_outcome_lambda_response_factory(
    status_code: int, severity: str, code: str, diagnostics: str
) -> Dict[str, Any]:
    return {
        "statusCode": status_code,
        "body": OperationOutcome(
            issue=[
                OperationOutcomeIssue(
                    severity=severity,
                    code=code,
                    diagnostics=diagnostics,
                )
            ]
        ).json(),
    }
