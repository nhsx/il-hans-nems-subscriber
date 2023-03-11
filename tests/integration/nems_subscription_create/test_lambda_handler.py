import os
from unittest.mock import MagicMock

import pytest

from src.nems_subscription_create.app import lambda_handler

TEST_DATA_PATH = f"{os.path.dirname(__file__)}/inputs/"


@pytest.mark.parametrize(
    "patient_data_file_path",
    [TEST_DATA_PATH + fn for fn in os.listdir(TEST_DATA_PATH) if "broken" not in fn],
)
@pytest.mark.vcr
def test_working_patient_data(patient_data_file_path: str):
    with open(patient_data_file_path, "r") as f:
        body = f.read()

    response = lambda_handler({"body": body}, MagicMock())
    assert response["statusCode"] == 201


@pytest.mark.parametrize(
    "patient_data_file_path",
    [TEST_DATA_PATH + fn for fn in os.listdir(TEST_DATA_PATH) if "broken" in fn],
)
@pytest.mark.vcr
def test_broken_patient_data(patient_data_file_path: str):
    with open(patient_data_file_path, "r") as f:
        body = f.read()

    response = lambda_handler({"body": body}, MagicMock())
    assert response["statusCode"] != 201
