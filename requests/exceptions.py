from .models import ALLOWED_METHODS


class BaseRequestException(Exception):
    def __init__(self, message: str = "An exception occured"):
        self.message = message
        super().__init__(self.__str__())
        
    def __str__(self):
        return self.message
    

class RequestFailure(BaseRequestException):
    def __init__(self, message: str = "The request has failed"):
        self.message = message
        super().__init__(self.__str__())


class MethodError(BaseRequestException):
    def __str__(self):
        return f"Unsupported HTTP method: '{self.method}'. Allowed methods are: [{', '.join(ALLOWED_METHODS.__args__)}]"


class OptionsError(BaseRequestException):
    def __init__(self, message:str = "Options got unexpected value"):
        super().__init__(message)
        
        
class ParsingError(Exception):
    def __init__(self, message: str = "The parsing has failed"):
        self.message = message
        super().__init__(self.__str__())

    def __str__(self):
        return self.message