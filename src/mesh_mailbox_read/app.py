# import requests


def lambda_handler(event, context):
    """Sample pure Lambda function

    Parameters
    ----------
    event: dict, required
        EventBridge Event Info

        Event doc: https://docs.aws.amazon.com/lambda/latest/dg/services-cloudwatchevents.html

    context: object, required
        Lambda Context runtime methods and attributes

        Context doc: https://docs.aws.amazon.com/lambda/latest/dg/python-context-object.html
    """

    # TODO: read from MESH inbox and write output to the queue

    return None
