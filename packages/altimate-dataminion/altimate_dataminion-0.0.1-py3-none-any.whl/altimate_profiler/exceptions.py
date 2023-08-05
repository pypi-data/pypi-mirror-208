class AltimateContractRegistryHTTPException(Exception):
    """
    Raised when the Altimate Contract Registry returns an error.
    """

    pass


class AltimateContractRegistryConnectionError(Exception):
    """
    Raised when the connection to the Altimate Contract Registry fails.
    """

    pass


class AltimateProfilerException(Exception):
    """
    Raised when the Altimate Profiler encounters an error.
    """

    pass


class AltimateContractRegistryUnknownException(Exception):
    """
    Raised when an unknown exception occurs
    """

    pass


class AltimateDataStoreNotSupported(Exception):
    """
    Raised when the data store is not supported
    """

    pass


class AltimateDataStoreConnectionException(Exception):
    """
    Raised when the data store is not supported
    """

    pass


class AltimateConfigNotFoundError(Exception):
    """
    Raised when the request to the Altimate Contract Registry fails.
    """

    pass


class AltimateContractRegistryBadRequestError(Exception):
    pass


class AltimateUnsupportedCollectorTypeError(Exception):
    pass


class AltimateInvalidInputException(Exception):
    pass


class AltimateRegistryNotFoundError(Exception):
    pass


class AltimateJSONFileNotLoadingError(Exception):
    pass
