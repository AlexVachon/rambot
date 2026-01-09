import typing
import hashlib
from datetime import date, datetime, timezone

from pydantic import BaseModel, Field, field_validator
from enum import Enum


class Document(BaseModel):
    """
    A model representing a document with a unique link.

    This class is designed to represent a document with a link. It provides methods
    to convert the document to a dictionary, compare documents, and enable usage in
    hash-based collections such as sets and dictionaries.

    Attributes:
        link (str): The unique link associated with the document.

    Methods:
        to_dict() -> dict:
            Converts the document instance into a dictionary representation.
        
        __str__() -> str:
            Returns a human-readable string representation of the document.
        
        __eq__(other: object) -> bool:
            Determines if two Document instances are equal based on their link.
        
        __hash__() -> int:
            Computes a hash value for the document based on its link, making it hashable.
    """

    link: str = Field("", alias="link")
    

    def to_dict(self) -> typing.Dict[str, typing.Any]:
        """
        Converts the document to a dictionary representation.

        This method serializes the `Document` instance into a dictionary format,
        allowing easy conversion to JSON or storage in structured data formats.

        Returns:
            dict: A dictionary representation of the document, containing its attributes.
        """
        return self.model_dump()

    def __str__(self) -> str:
        """
        Returns a string representation of the document.

        This method provides a readable representation of the document,
        primarily displaying its link.

        Returns:
            str: A formatted string containing the document's link.
        """
        return f"link: {self.link}"

    def __eq__(self, other: object) -> bool:
        """
        Checks equality between two Document instances.

        Two Document instances are considered equal if they have the same link.

        Args:
            other (object): The object to compare with the current instance.

        Returns:
            bool: True if both instances have the same link, False otherwise.
        """
        if isinstance(other, Document):
            return self.link == other.link
        return False
    
    def __hash__(self) -> int:
        """
        Generates a hash value for the document.

        This method allows Document instances to be used in sets and as dictionary keys
        by computing a hash based on the `link` attribute.

        Returns:
            int: The computed hash value of the document.
        """
        return hash(self.link)


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
        log_directory (str): The file path to store logs, defaults to the current directory.
        enable_file_logging (bool): Whether to save logs for this mode.
        log_file_name (Optional[str]): The output path for logs, can be None to use a default path.
    """
    name: str = Field(alias="name")
    
    func: typing.Optional[typing.Callable] = Field(None, alias="func")
    input: typing.Optional[typing.Union[str, typing.Callable[[], typing.List[typing.Dict[str, typing.Any]]]]] = Field(None, alias="input")
    save: typing.Optional[typing.Callable[[typing.Any], None]] = Field(None, alias="save")
    # document_input: typing.Optional[typing.Type[Document]] = Field(None, alias="document_input")
    
    document_output: typing.Type[Document] = Field(Document, alias="document_output")
    expected_input_type: typing.Optional[typing.Type] = Field(None, alias="expected_input_type")
    
    log_directory: str   = Field(".", alias="log_directory")
    enable_file_logging: bool = Field(False, alias="enable_file_logging")
    log_file_name: typing.Optional[str] = Field(None, alias="log_file_name")
    
    @field_validator("log_file_name", mode="before")
    @classmethod
    def set_default_logs(cls, v, values):
        """
        Sets a default log output path if not provided.

        If `log_file_name` is not provided, the function sets the default log path based on the
        mode name and the current date, appending it to the specified directory path.

        Args:
            v (str or None): The provided value for the logs output path.
            values (dict): The values from the mode configuration.

        Returns:
            str: The default or provided log output path.
        """
        path = values.data.get("log_directory", ".")
        
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
    _output_registry: typing.Dict[typing.Type[Document], str] = {}

    @classmethod
    def register(
        cls,
        name: str, 
        func: typing.Optional[typing.Callable] = None,
        document_output: typing.Type[Document] = Document,
        expected_input_type: typing.Optional[typing.Type] = None,
        input: typing.Optional[typing.Union[str, typing.Callable]] = None,
        save: typing.Optional[typing.Callable[[typing.Any], None]] = None,
        enable_file_logging: bool = False,
        log_file_name: typing.Optional[str] = None,
        log_directory: str = '.'
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
            enable_file_logging (bool): Whether to save logs for this mode.
            log_file_name (Optional[str]): The output path for logs.
            log_directory (str): The directory path for logs, defaults to the current directory.
        """
        if document_output and issubclass(document_output, Document):
            cls._output_registry[document_output] = name
        
        if name not in cls._modes:
            cls._modes[name] = Mode(
                name=name,
                func=func, 
                document_output=document_output,
                expected_input_type=expected_input_type,
                input=input, 
                save=save,
                enable_file_logging=enable_file_logging,
                log_file_name=log_file_name,
                log_directory=log_directory
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
    
    @classmethod
    def get_auto_input(cls, mode_name: str) -> typing.Optional[typing.Union[str, typing.Callable]]:
        mode = cls.get_mode(mode_name)
        
        if mode.input:
            return mode.input
            
        if mode.expected_input_type in cls._output_registry:
            source_mode = cls._output_registry[mode.expected_input_type]
            return f"{source_mode}.json"
        
        return None


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


class ScrapedDocument(BaseModel):
    """
    A model representing a scraped document, including its source, origin, unique identifier, and creation timestamp.
    
    Attributes:
        source (Optional[str]): The source from which the document was scraped. Defaults to None.
        origin (Dict[str, str]): A dictionary containing information about the origin of the document, such as the scraping mode. Defaults to an empty dictionary.
        document (Document): The actual Document object representing the scraped content.
        unique_id (str): A unique identifier for the document, generated using an MD5 hash of the document's link.
        created_at (datetime): The timestamp when the document was created, defaulting to the current UTC time.

    Methods:
        generate_unique_id(cls, link: str) -> str:
            Generates a unique MD5 hash ID for a document based on its link.
        
        from_document(cls, document: Document, source: str, mode: str) -> "ScrapedDocument":
            Creates an instance of the ScrapedDocument class from a Document object.
        
        to_dict(self) -> Dict[str, Any]:
            Converts the ScrapedDocument instance into a dictionary format, with the creation timestamp formatted as a string.
    """
    source: typing.Optional[str] = Field(None, alias="source")
    origin: typing.Dict[str, str] = Field({}, alias="origin")
    
    document: Document = Field(Document(), alias="document")
    
    unique_id: str = Field(default_factory=lambda: hashlib.md5().hexdigest())
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def generate_unique_id(cls, link: str) -> str:
        return hashlib.md5(link.encode()).hexdigest()
    
    @classmethod
    def from_document(
        cls, document: Document, source: str, mode: str
    ) -> "ScrapedDocument":
        return cls(
            source=source,
            origin={"mode": mode},
            document=document,
            unique_id=cls.generate_unique_id(document.link),
            created_at=datetime.now(timezone.utc)
        )
    
    def to_dict(self) -> typing.Dict[str, typing.Any]:
        return {
            "source": self.source,
            "origin": self.origin,
            "document": self.document.to_dict(),
            "unique_id": self.unique_id,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S.%f%z')
        }
    

mode_manager = ScraperModeManager()