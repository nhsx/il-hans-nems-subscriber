# import requests


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        SQS Queue Messages

        Event doc: https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    """

    # TODO: lookup correct care provider from the database and send an email

    return None
