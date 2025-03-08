# botasaurus/exceptions.py

class DriverError(Exception):
    """
    Base exception class for driver-related errors.

    This exception serves as the base class for any errors related to the driver
    in the context of web scraping or automation. It can be extended to create more
    specific exceptions related to driver issues.

    Usage:
        raise DriverError("An error occurred with the driver.")
    """
    pass
