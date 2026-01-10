from typing import Literal


class BaseRequestException(Exception):
    """
    Base exception class for handling general request-related errors.

    Inherits from the built-in `Exception` class and provides a custom message
    for the exception.

    Attributes:
        message (str): The error message to be shown when the exception is raised.
    """
    def __init__(self, message: str = "An exception occurred"):
        """
        Initializes the exception with a given message.

        Args:
            message (str): The custom error message. Defaults to "An exception occurred".
        """
        self.message = message
        super().__init__(self.__str__())

    def __str__(self):
        """
        Returns the string representation of the exception.

        Returns:
            str: The message associated with the exception.
        """
        return self.message
    


class RequestFailure(BaseRequestException):
    """
    Exception raised when a request fails.

    Inherits from `BaseRequestException` and provides a default message for request failures.

    Attributes:
        message (str): The error message for the request failure. Defaults to "The request has failed".
    """
    def __init__(self, message: str = "The request has failed"):
        """
        Initializes the exception with a given message.

        Args:
            message (str): The custom error message. Defaults to "The request has failed".
        """
        self.message = message
        super().__init__(self.__str__())


class MethodError(BaseRequestException):
    """
    Exception raised when an unsupported HTTP method is used.

    Inherits from `BaseRequestException` and customizes the string representation 
    to include the unsupported method and the allowed methods.

    Attributes:
        method (str): The unsupported HTTP method that caused the error.
    """
    def __str__(self):
        """
        Returns the string representation of the exception, including the unsupported method.

        Returns:
            str: The message indicating the unsupported method and the allowed methods.
        """
        return f"Unsupported HTTP method: '{self.method}'. Allowed methods are: [{', '.join(Literal["GET", "POST"].__args__)}]"


class OptionsError(BaseRequestException):
    """
    Exception raised when an unexpected value is encountered in options.

    Inherits from `BaseRequestException` and provides a default message for options errors.

    Attributes:
        message (str): The error message for the options error. Defaults to "Options got unexpected value".
    """
    def __init__(self, message: str = "Options got unexpected value"):
        """
        Initializes the exception with a given message.

        Args:
            message (str): The custom error message. Defaults to "Options got unexpected value".
        """
        super().__init__(message)
        
        
class ParsingError(Exception):
    """
    Exception raised when parsing fails.

    This class inherits directly from the built-in `Exception` and provides a custom message
    for parsing errors.

    Attributes:
        message (str): The error message for the parsing failure. Defaults to "The parsing has failed".
    """
    def __init__(self, message: str = "The parsing has failed"):
        """
        Initializes the exception with a given message.

        Args:
            message (str): The custom error message. Defaults to "The parsing has failed".
        """
        self.message = message
        super().__init__(self.__str__())

    def __str__(self):
        """
        Returns the string representation of the exception.

        Returns:
            str: The message associated with the exception.
        """
        return self.message
