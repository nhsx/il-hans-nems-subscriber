class ManagementInterfaceApiClientException(Exception):
    pass


class CareProviderLocationNotFound(ManagementInterfaceApiClientException):
    pass


class ManagementInterfaceNotAvailable(ManagementInterfaceApiClientException):
    pass
