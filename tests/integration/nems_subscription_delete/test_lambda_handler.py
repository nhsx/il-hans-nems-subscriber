from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from subscription_delete.app import lambda_handler


@pytest.mark.parametrize(
    "subscription_id", (str(uuid4()) + "a", "12345", "AEIOUY", str(uuid4())[:-1])
)
def test_lambda_handler__invalid_subscription_id(subscription_id: str):
    event = {"pathParameters": {"id": subscription_id}}
    response = lambda_handler(event, MagicMock())
    assert response["statusCode"] >= 500


def test_lambda_handler__no_subscription_id():
    event = {"pathParameters": {}}
    response = lambda_handler(event, MagicMock())
    assert response["statusCode"] >= 500
