import os
from unittest.mock import MagicMock

import pytest

from src.nems_subscription_create.app import lambda_handler

BROKEN_PATIENTS_TEST_DATA_PATH = f"{os.path.dirname(__file__)}/inputs/broken-patients/"
VALID_PATIENTS_TEST_DATA_PATH = f"{os.path.dirname(__file__)}/inputs/valid-patients/"


@pytest.mark.parametrize(
    "patient_data_file_path",
    [
        VALID_PATIENTS_TEST_DATA_PATH + fn
        for fn in os.listdir(VALID_PATIENTS_TEST_DATA_PATH)
    ],
)
@pytest.mark.vcr
def test_valid_patient_data(patient_data_file_path: str):
    with open(patient_data_file_path, "r") as f:
        body = f.read()

    response = lambda_handler({"body": body}, MagicMock())
    assert response["statusCode"] == 201


@pytest.mark.parametrize(
    "patient_data_file_path",
    [
        BROKEN_PATIENTS_TEST_DATA_PATH + fn
        for fn in os.listdir(BROKEN_PATIENTS_TEST_DATA_PATH)
    ],
)
@pytest.mark.vcr
def test_broken_patient_data(patient_data_file_path: str):
    with open(patient_data_file_path, "r") as f:
        body = f.read()

    response = lambda_handler({"body": body}, MagicMock())
    assert response["statusCode"] != 201
