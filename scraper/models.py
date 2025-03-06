import typing
from datetime import date

from pydantic import BaseModel, Field, field_validator
from enum import Enum


class Document(BaseModel):
    """
    A model representing a document with a link.

    This class is used to represent a document with a link. It includes a method
    to convert the document to a dictionary and a string representation of the document.

    Attributes:
        link (str): The link to the document.
    """
    link: str

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Converts the document to a dictionary.

        Returns:
            dict: A dictionary representation of the document.
        """
        return self.model_dump()

    def __str__(self):
        """
        Returns a string representation of the document.

        Returns:
            str: The string representation of the document with its link.
        """
        return f"link: {self.link}"


class Mode(BaseModel):
    """
    A model representing a mode of operation for a scraper or process.

    This class defines the configuration and parameters associated with a specific mode,
    including the function to be executed, input handling, logging options, and a save function.

    Attributes:
        name (str): The name of the mode.
        func (Optional[Callable]): An optional function to execute in this mode.
        input (Optional[Union[str, Callable]]): The input for the mode, which can be a string or a callable that returns a list of dictionaries.
        save (Optional[Callable[[Any], None]]): An optional function to save the results of this mode.
        document_input (Optional[Type[Document]]): The document input type associated with the mode.
        path (str): The file path to store logs, defaults to the current directory.
        save_logs (bool): Whether to save logs for this mode.
        logs_output (Optional[str]): The output path for logs, can be None to use a default path.
    """
    name: str = Field(alias="name")
    
    func: typing.Optional[typing.Callable] = Field(None, alias="func")
    input: typing.Optional[typing.Union[str, typing.Callable[[], typing.List[typing.Dict[str, typing.Any]]]]] = Field(None, alias="input")
    save: typing.Optional[typing.Callable[[typing.Any], None]] = Field(None, alias="save")
    document_input: typing.Optional[typing.Type[Document]] = Field(None, alias="document_input")
    
    path: str   = Field(".", alias="path")
    save_logs: bool = Field(False, alias="save_logs")
    logs_output: typing.Optional[str] = Field(None, alias="logs_output")
    
    @field_validator("logs_output", mode="before")
    @classmethod
    def set_default_logs(cls, v, values):
        """
        Sets a default log output path if not provided.

        If `logs_output` is not provided, the function sets the default log path based on the
        mode name and the current date, appending it to the specified directory path.

        Args:
            v (str or None): The provided value for the logs output path.
            values (dict): The values from the mode configuration.

        Returns:
            str: The default or provided log output path.
        """
        path = values.data.get("path", ".")
        
        if v is None:
            mode = values.data.get('name')
            today = date.today().strftime("%Y-%m-%d")
            return f"{path}/{mode}_{today}.log"
        
        return f"{path}/{v}"


class ScraperModeManager:
    """
    A class to manage scraper modes.

    This class provides functionality to register, validate, and retrieve modes for scraping operations.
    It also handles the retrieval of associated functions and configurations.

    Attributes:
        _modes (dict): A dictionary holding the registered modes.
    """
    _modes = {}

    @classmethod
    def register(
        cls, 
        name: str, 
        func: typing.Optional[typing.Callable] = None, 
        input: typing.Optional[typing.Union[str, typing.Callable[[], typing.List[typing.Dict[str, typing.Any]]]]] = None,
        save: typing.Optional[typing.Callable[[typing.Any], None]] = None,
        document_input: typing.Optional[typing.Type[Document]] = None,
        save_logs: bool = False,
        logs_output: typing.Optional[str] = None,
        path: str = '.'
    ):
        """
        Registers a new mode for the scraper.

        This method allows you to register a new mode by providing a name, function, input parameters,
        a save function, logging options, and other configurations.

        Args:
            name (str): The name of the mode.
            func (Optional[Callable]): An optional function to associate with the mode.
            input (Optional[Union[str, Callable]]): The input for the mode, which can be a string or a callable.
            save (Optional[Callable[[Any], None]]): A function to save the results of this mode.
            document_input (Optional[Type[Document]]): The document type associated with the mode.
            save_logs (bool): Whether to save logs for this mode.
            logs_output (Optional[str]): The output path for logs.
            path (str): The directory path for logs, defaults to the current directory.
        """

        if name not in cls._modes:
            cls._modes[name] = Mode(
                name=name,
                func=func, 
                input=input, 
                save=save,
                document_input=document_input, 
                save_logs=save_logs,
                logs_output=logs_output,
                path=path
            )

    @classmethod
    def all(cls):
        """
        Returns the list of all registered modes.

        Returns:
            list: A list of mode names.
        """
        return list(cls._modes.keys())

    @classmethod
    def validate(cls, mode: str):
        """
        Validates that the provided mode is registered.

        Args:
            mode (str): The mode name to validate.

        Raises:
            ValueError: If the mode is not registered.
        """
        if mode not in cls._modes:
            raise ValueError(f"Mode '{mode}' non reconnu. Modes disponibles: {cls.all()}")

    @classmethod
    def get_mode(cls, mode: str) -> Mode:
        """
        Retrieves the mode by its name.

        Args:
            mode (str): The mode name.

        Returns:
            Mode: The mode object associated with the name.

        Raises:
            ValueError: If the mode is not registered.
        """
        cls.validate(mode)
        return cls._modes[mode]

    @classmethod
    def get_func(cls, mode: str) -> typing.Optional[typing.Callable]:
        """
        Retrieves the function associated with a mode.

        Args:
            mode (str): The mode name.

        Returns:
            Callable: The function associated with the mode.

        Raises:
            ValueError: If no function is associated with the mode.
        """
        cls.validate(mode)
        mode_info = cls.get_mode(mode)
        func = mode_info.func
        if func is None:
            raise ValueError(f"Aucune fonction associée au mode '{mode}'")
        return func


class ModeStatus(Enum):
    """
    Enum to represent the possible statuses of a mode's result.

    Attributes:
        SUCCESS (str): Represents a successful mode operation.
        ERROR (str): Represents an error during the mode operation.
    """
    SUCCESS = "success"
    ERROR = "error"


class ModeResult(BaseModel):
    """
    A model representing the result of a mode operation.

    This model holds the status of the operation (success or error) and an optional message.

    Attributes:
        status (ModeStatus): The status of the mode operation (success or error).
        message (Optional[str]): An optional message related to the mode result.
    """
    status: ModeStatus = Field(ModeStatus.ERROR, alias="status")
    message: typing.Optional[str] = Field(None, alias="message")
