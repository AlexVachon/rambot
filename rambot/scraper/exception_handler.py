import typing
import traceback
import inspect

from loguru import logger


class ExceptionHandler:
    def __init__(self, must_raise_exceptions: typing.List[typing.Type[Exception]] = [Exception]):
        self.logger = logger
        self.must_raise = must_raise_exceptions

    def handle(self, e: Exception) -> None:
        """
        Handles the exception by logging it and performing specific actions such as 
        sending alerts, or deciding whether the exception should be raised again.

        Args:
            e (Exception): The exception to handle.
        """
        
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name

        error_message = f"Error in {function_name}: {str(e)}"
        traceback_details = traceback.format_exc()

        self.logger.warning(f"{error_message}\n{traceback_details}")

        if any(isinstance(e, exc_type) for exc_type in self.must_raise):
            raise e
