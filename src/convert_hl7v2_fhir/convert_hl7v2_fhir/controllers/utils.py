from typing import Dict, Any


def is_nhs_number_valid(nhs_number: str) -> bool:
    # check length
    if len(nhs_number) != 10:
        return False

    # perform modulus 11 check (see https://www.datadictionary.nhs.uk/attributes/nhs_number.html)
    check_digit = nhs_number[9]
    main_part = nhs_number[0:9]

    sum = 0
    for digit_index in range(0, 9):
        sum += (10 - digit_index) * int(main_part[digit_index])
    calculated_check_digit = 11 - (sum % 11)

    if calculated_check_digit == 10:
        return False
    elif calculated_check_digit == 11:
        calculated_check_digit = 0

    return str(calculated_check_digit) == check_digit


def hl7v2_lambda_response_factory(body: str) -> Dict[str, Any]:
    return {
        "statusCode": 200,
        "headers": {"content-type": "x-application/hl7-v2+er; charset=utf-8"},
        "body": body,
    }
