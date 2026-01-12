from functools import wraps
from inspect import signature, isclass
from typing import (
    Callable, List,
    Optional, Union, Type,
    Any, Set,
    get_type_hints, get_origin, get_args
)

from .models import Document, ScrapedDocument, Mode, mode_manager
from ..types import IScraper

def _extract_doc_type(func: Callable) -> Type[Document]:
    """Helper to find the Document subclass in return hints."""
    hints = get_type_hints(func)
    ret = hints.get('return', Document)
    
    origin, args = get_origin(ret), get_args(ret)
    if origin in (list, List) and args:
        ret = args[0]
        
    return ret if isclass(ret) and issubclass(ret, Document) else Document


def pipeline(*modes: str):
    """
    Class decorator to define the sequence of data flow for a Scraper.\n
    Validates that each mode exists and that type hints are compatible.
    """
    def decorator(cls):
        mode_manager.set_pipeline(*modes)
        return cls
    return decorator


def bind(
    mode: str,
    *,
    input: Optional[Union[str, Callable]] = None,
    document_output: Optional[Type[Document]] = None,
    save: Optional[Callable[[Any], None]] = None,
    enable_file_logging: bool = False,
    log_file_name: Optional[str] = None,
    log_directory: str = "."
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Registers a function as a scraper mode and configures its automated data pipeline.

    This decorator orchestrates the connection between scraping phases. It enables 
    "Magic" auto-discovery: if a mode requires a specific Document subclass as an 
    argument (e.g., `City`), the manager automatically identifies the mode that 
    produces that type and links its JSON output as the input source.

    Args:
        mode (str): The CLI name for the mode (e.g., '--mode listing').
        input (Optional[Union[str, Callable]]): The input source. Can be:
            - A filename (e.g., 'cities.json').
            - A callable that returns a list of dictionaries.
            - If None, Rambot uses the type hint of the first argument to 
              auto-detect the matching output file from the Type Registry.
        document_output (Optional[Type[Document]]): The class used to save results.
            If None, Rambot extracts this from the return type hint (e.g., -> list[City]).
            This class acts as a key in the Type Registry to link dependent modes.
        save (Optional[Callable[[Any], None]]): Optional custom function to persist results.
        enable_file_logging (bool): Whether to create a dedicated log file for this mode.
        log_file_name (Optional[str]): Custom log filename. If None, defaults to 
            '{mode}_{date}.log'.
        log_directory (str): Directory for log storage. Defaults to current directory.

    Returns:
        Callable: The original function, registered within the ScraperModeManager.

    Examples:
        **Option 1: Auto-Discovery via Subclasses (Recommended)**
        ```python
        class City(Document): name: str

        @bind("cities")
        def get_cities(self) -> list[City]:
            return [City(link="...", name="Vancouver")]

        @bind("listing")
        def get_listings(self, city: City):
            # 'listing' automatically reads 'cities.json' because it needs 'City'
            self.load_page(city.link)
        ```

        **Option 2: Manual Input (For Generic Documents)**
        ```python
        @bind("details", input="listing.json")
        def get_details(self, doc: Document):
            self.load_page(doc.link)
        ```
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        final_output_type = document_output or _extract_doc_type(func)
        
        sig = signature(func)
        input_type = None
        for name, param in sig.parameters.items():
            if name != 'self' and param.annotation is not param.empty:
                input_type = param.annotation
                break
            
        mode_manager.register(
            name=mode,
            func=func,
            input=input,
            document_output=final_output_type,
            expected_input_type=input_type,
            save=save,
            enable_file_logging=enable_file_logging,
            log_file_name=log_file_name,
            log_directory=log_directory
        )
        return func

    return decorator


def scrape(func: Callable[..., List[Document]]) -> Callable[..., List[Document]]:
    """
    A decorator for handling the scraping process in a class inheriting from Scraper.

    This decorator ensures that the function is executed within a properly managed scraping 
    session, including validation, logging, input handling, and saving results.

    Args:
        func (Callable): The function to be decorated, expected to process and return a list of `Document` objects.

    Returns:
        Callable: A wrapped function that manages the scraping process.

    Raises:
        TypeError: If the decorator is used on a class that does not inherit from `Scraper`.
        ValueError: If no function is associated with the current mode.
        TypeError: If the function does not return a list of `Document` instances.

    Functionality:
        - Validates that the `Scraper` class is being used.
        - Retrieves the mode's configuration from `ScraperModeManager`.
        - Processes input data, either from a callable or a file.
        - Calls the mode’s associated function, ensuring it returns a list of `Document` objects.
        - Handles logging and exceptions.
        - Saves the results using the mode's `save` function (if provided) and the scraper’s `save` method.

    Example:
        ```python
        class MyScraper(Scraper):
            @scrape
            def my_scraper_function(self, document: Document):
                # Process the document and return results
                return document
        ```
    """
    @wraps(func)
    def wrapper(self: Type[IScraper], *args, **kwargs) -> List[Document]:
        self.mode_manager.validate(self.mode)
        mode_info = self.mode_manager.get_mode(self.mode)
        method = mode_info.func.__get__(self, type(self))
        results: Set[Document] = set()

        try:
            self.open_browser()
            
            if (url := getattr(self.args, "url", None)):
                input_list = [{"document": {"link": url}}]
            else:
                source = mode_manager.get_auto_input(self.mode)
                input_list = source(self) if callable(source) else self.read(filename=source) if source else []

            if input_list:
                for data in input_list:
                    doc = self.create_document(obj=data, document=mode_info.expected_input_type or Document)
                    try:
                        res = method(doc, *args, **kwargs)
                        if res: results.update(res if isinstance(res, (list, set)) else {res})
                    except Exception as e:
                        self.logger.error(f"Error processing {doc}: {e}")
                    self.wait(1, 2)
            else:
                res = method(*args, **kwargs)
                if res: results.update(res if isinstance(res, (list, set)) else {res})

        finally:
            if results:
                if mode_info.save: mode_info.save(self, list(results))
                self.save(data=[ScrapedDocument.from_document(r, self.__class__.__name__, self.mode) for r in results])
            
            self.close_browser()
            return list(results)

    return wrapper
