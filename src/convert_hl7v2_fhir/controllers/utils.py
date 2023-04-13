def is_nhs_number_valid(nhs_number: str) -> bool:
    if len(nhs_number) != 10:
        return False

    # perform modulus 11 check (see https://www.datadictionary.nhs.uk/attributes/nhs_number.html)
    check_digit = nhs_number[9]
    main_part = nhs_number[0:9]

    sum_of_digits = 0
    for digit_index in range(0, 9):
        sum_of_digits += (10 - digit_index) * int(main_part[digit_index])
    calculated_check_digit = 11 - (sum_of_digits % 11)

    if calculated_check_digit == 10:
        return False
    elif calculated_check_digit == 11:
        calculated_check_digit = 0

    return str(calculated_check_digit) == check_digit
