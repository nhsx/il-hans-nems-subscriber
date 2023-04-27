import os
from unittest.mock import MagicMock
from uuid import UUID

import pytest
from pytest_mock import MockFixture
from nems_subscription_create.app import lambda_handler

BROKEN_PATIENTS_TEST_DATA_PATH = "tests/_inputs/broken-patients/"
VALID_PATIENTS_TEST_DATA_PATH = "tests/_inputs/valid-patients/"


@pytest.mark.parametrize(
    "patient_data_file_path",
    [
        VALID_PATIENTS_TEST_DATA_PATH + fn
        for fn in os.listdir(VALID_PATIENTS_TEST_DATA_PATH)
    ],
)
@pytest.mark.vcr("casette.yml")
def test_valid_patient_data(patient_data_file_path: str, mocker: MockFixture):
    with open(patient_data_file_path, "r") as f:
        body = f.read()

    response = lambda_handler({"body": body}, MagicMock())
    assert response["statusCode"] == 201
    assert UUID(response["headers"]["X-Subscription-Id"])


@pytest.mark.parametrize(
    "patient_data_file_path",
    [
        BROKEN_PATIENTS_TEST_DATA_PATH + fn
        for fn in os.listdir(BROKEN_PATIENTS_TEST_DATA_PATH)
    ],
)
@pytest.mark.vcr("casette.yml")
def test_broken_patient_data(patient_data_file_path: str):
    with open(patient_data_file_path, "r") as f:
        body = f.read()

    response = lambda_handler({"body": body}, MagicMock())
    assert response["statusCode"] != 201
