# Hospital Activity Notification Service (HANS) - Subscription Management API

The Hospital Activity Notification Service forwards relevant internal messages from hospital systems to domiciliary care providers, to let them know when their clients have been admitted. It is a pilot project over a limited period to assess the benefits of providing this information in a timely way.

This project provides the integration with the Personal Demographics Service (PDS), to check subscriptions are being created for the right patients and the "publish" logic to queue up and send messages to care providers.

Related projects are:
* [Management Interface](https://github.com/nhsx/il-hans-management-interface) (lookup service between NHS Number and care provider email address)
* [Infrastructure](https://github.com/nhsx/il-hans-infrastructure) (creates relevant non-serverless infrastructure)

It is an [AWS SAM](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) application written in Python.

The pilot is being run by the [NHS Innovation Lab](https://transform.england.nhs.uk/innovation-lab/).

## Prerequisites
You will need access to the [Personal Demographics Service (PDS) FHIR API integration environment](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir#api-description__environments-and-testing). This will provide you with the following:
* PDS API public/private key pair
* PDS API JWKS hosted online
* PDS API Key

You will need a [GOV.UK Notify API Key](https://www.notifications.service.gov.uk/). This will provide you with:
* GOV.UK Notify API Key

You will need to install the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/prerequisites.html). 

Note, that using this with AWS SSO requires a "legacy" profile - you can create this by leaving "SSO session name" blank when running `aws configure sso`.

To run the code locally you will need to install [Docker Engine](https://docs.docker.com/engine/) and ensure it is running.

## Usage
Set up a copy of `envars.json` and add the information from above.

You can run the code locally using `sam local start-api --env-vars envars.json`. This will set up a local endpoint at `127.0.0.1:3000`.

In production, you will need to use production APIs, run the software in an environment that has been CHECK pentration tested and achieve IG and DCB0129 (Clinical Safety) approval.

## Documentation
The API is documented in the OpenAPI format [on the tech docs website](https://nhsx.github.io/il-hans-infrastructure/serverless-api/).


## Contribution
Contact [Alex Young](mailto:alex.young12@nhs.net) for further information if you would like to contribute.