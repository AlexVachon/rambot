from functools import wraps
from inspect import signature, isclass
from typing import (
    Callable, Dict, List,
    Optional, Union, Type,
    Any, Set,
    get_type_hints, get_origin, get_args
)

from .models import Document, ScrapedDocument, mode_manager
from ..types import IScraper

def _extract_doc_type(func: Callable) -> Type[Document]:
    """Helper to find the Document subclass in '-> list[City]'"""
    try:
        hints = get_type_hints(func)
        ret = hints.get('return')
        if not ret: return Document

        origin = get_origin(ret)
        args = get_args(ret)
        if (origin is list or origin is List) and args:
            return args[0] if isclass(args[0]) and issubclass(args[0], Document) else Document
            
        # Handles direct return: -> Restaurant
        if isclass(ret) and issubclass(ret, Document):
            return ret
    except: pass
    return Document


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

        def prepare_input(mode_info) -> List[Any]:
            # 1. Priority: CLI URL override
            if (url := getattr(self.args, "url", None)):
                # Uses the detected output type for the current mode
                return [mode_info.document_output(link=url).to_dict()]

            # 2. Logic: Automatic input discovery based on Type Registry
            input_source = mode_manager.get_auto_input(mode_info.name)

            if not input_source:
                return []
            
            if callable(input_source):
                return input_source(self)

            # Returns the data from the detected file (e.g., 'cities.json')
            return self.read(filename=input_source)

        def validate_results(items: Any) -> Set[Document]:
            """Ensure returned items are a set of Documents."""
            if not items:
                return set()
            if not isinstance(items, (list, set)):
                items = {items}
            else:
                items = set(items)
            if not all(isinstance(r, Document) for r in items):
                raise TypeError(f"Expected List[Document], but got {type(items)} with elements {items}")
            return items

        results: Set[Document] = set()

        try:
            self.mode_manager.validate(self.mode)
            mode_info = self.mode_manager.get_mode(self.mode)
            
            if mode_info.func is None:
                raise ValueError(f"No function associated with mode '{self.mode}'")

            method = mode_info.func.__get__(self, type(self))
            self.logger.debug(f"Running scraper mode \"{self.mode}\"")

            self.open_browser()

            input_list = prepare_input(mode_info)

            # Check if the mode expects a positional argument (like 'city: City')
            if input_list:
                for data in input_list:
                    # Use the expected type hint (City) discovered by @bind
                    input_cls = mode_info.expected_input_type or Document
                    doc = self.create_document(obj=data, document=input_cls)
                    
                    self.logger.debug(f"Processing {doc}")

                    try:
                        # This passes 'doc' as the required positional argument
                        result = method(doc, *args, **kwargs)
                        results.update(validate_results(result))
                    except Exception as e:
                        self.logger.error(f"Error processing {doc}: {e}")

                    self.wait(1, 2)
            else:
                result = method(*args, **kwargs)
                results.update(validate_results(result))

        except Exception as e:
            results = set()
            self.exception_handler.handle(e)
        finally:
            # Ensure mode_info exists before accessing save or save logic
            if 'mode_info' in locals():
                if mode_info.save is not None:
                    mode_info.save(self, list(results))

                self.save(
                    data=[
                        ScrapedDocument.from_document(
                            document=r, 
                            mode=self.mode, 
                            source=self.__class__.__name__
                        ) 
                        for r in results
                    ]
                )
            
            self.close_browser()
            return list(results)

    return wrapper