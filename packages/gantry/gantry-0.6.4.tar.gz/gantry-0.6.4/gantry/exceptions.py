class GantryException(Exception):
    """
    Base class for Gantry exceptions.
    """

    pass


class GantryLoggingException(GantryException):
    """
    Raised when logging invalid data.
    """

    pass


class GantryLoggingDataTypeError(GantryLoggingException):
    """
    Raised when Gantry cannot process datatype
    """

    pass


class ClientNotInitialized(GantryException):
    """
    Gantry client not initialized
    """

    def __init__(self):
        message = "Gantry client is not initialized. Did you call `gantry.init()`?"
        super(ClientNotInitialized, self).__init__(message)


class QueryError(GantryException):
    """
    Raised when a query doesn't have a result
    """

    pass


class GantryBatchCreationException(GantryException):
    """
    Raised when gantry failed to create batch
    """

    pass


class GantryRequestException(GantryException):
    """
    Raised when an API request returns an error.
    """

    def __init__(self, url: str, status_code: int, response_text: str) -> None:
        if status_code == 404:
            if "/api/v1/ingest/data-connectors" in url:
                msg = (
                    "Data connector exception. Ensure the parameters refer to an existing "
                    "data connector you have access to. Details: {}"
                ).format(response_text)
            else:
                msg = (
                    "A resource was not found while trying to access ({}). Ensure the parameters "
                    "refer to an existing resource you have access to. Details: {}"
                ).format(url, response_text)
        elif status_code == 429:
            if "/api/v1/ingest/data-connectors" in url:
                msg = (
                    "Data connector has hit the concurrency limit. Please reach out to Gantry "
                    + "support if you would like to raise this limit."
                )
            else:
                msg = (
                    "Logger has hit the rate limit. Please reach out to Gantry "
                    "support if you would like to raise this limit."
                )
        elif status_code == 401:
            msg = (
                "Authentication error. Ensure that you supplied a working API key by "
                "calling gantry.ready()."
            )
        elif status_code == 403:
            msg = (
                "Access denied. Check with your organization admin or Gantry support "
                "that you have the appropriate permissions to perform this action"
            )
        elif status_code >= 400 and status_code < 500:
            msg = (
                "Malformed data error. Ensure Gantry is receiving valid data. Details: {}"
            ).format(response_text)
        else:
            msg = "Internal Gantry error. Contact Gantry support for help."

        err_msg = "{} (Status code: {})".format(msg, status_code)
        self.status_code = status_code
        super().__init__(err_msg)


class DatasetDeletedException(GantryException):
    """
    Raised when an illegal dataset operation is attempted on a deleted dataset
    """

    pass


class CuratorNotFoundError(GantryException):
    """
    Raised when a curator is not found and thus cannot be enabled / disabled
    """

    pass


class DatasetCommitNotFoundError(GantryException):
    """
    Raised when a specific requested dataset commit is not found
    """

    pass


class DatasetNotFoundError(GantryException):
    """
    Raised when a specific requested dataset is not found
    """

    pass


class DatasetHeadOutOfDateException(GantryException):
    """
    Raised when a the head is out of date for a dataset operation
    """

    def __init__(self):
        message = "Local HEAD not up to date! Your local version is behind the remote"
        super().__init__(message)


class NoTabularDataError(GantryException):
    """
    Raised when there is no tabular data folder in a dataset
    """

    def __init__(self):
        message = (
            "No tabular data found in tabular_manifests folder! Please make sure that the"
            "tabular_manifests folder exists and contains at least one manifest file."
        )
        super().__init__(message)


class DataSchemaMismatchError(GantryException):
    """
    Raised when the dataset config schema disagrees with the csv content
    """

    def __init__(self):
        message = (
            "The dataset config schema disagrees with the data! "
            "Ensure that the columns in the dataset config match those in the tabular data files "
            "and that the types in the config are all correct."
        )
        super().__init__(message)
