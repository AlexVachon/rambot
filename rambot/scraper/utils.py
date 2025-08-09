from functools import wraps
from typing import Callable, Dict, List, Optional, Union, Type, Any, Set

from .models import Document, ScrapedDocument, mode_manager


def bind(
    mode: str, 
    input: Optional[Union[str, Callable[[], List[Dict[str, Any]]]]] = None,
    save: Optional[Callable[[Any], None]] = None,
    document_input: Optional[Type[Document]] = None,
    enable_file_logging: bool = True,
    log_file_name: Optional[str] = None,
    log_directory: str = "."
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    A decorator to register a function as a mode in the ScraperModeManager.

    This decorator allows binding a function to a specific mode with optional input processing, 
    saving functionality, logging configuration, and document input type.

    Args:
        mode (str): The name of the mode to register.
        input (Optional[Union[str, Callable]]): The input source for the mode, which can be:
            - A string representing an input source.
            - A callable that returns a list of dictionaries.
        save (Optional[Callable[[Any], None]]): A function to save the results of the mode.
        document_input (Optional[Type[Document]]): The document type associated with this mode.
        enable_file_logging (bool): Whether to enable logging for this mode.
        log_file_name (Optional[str]): The output path for logs. If None, a default path is used.
        log_directory (str): The directory path where logs should be stored. Defaults to the current directory.

    Returns:
        Callable: The original function, now registered as a mode.

    Example:
        ```python
        @bind(mode="extract_data", save=my_save_function, log_directory="logs/mode_cities")
        def extract():
            return {"data": "example"}
        ```
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        mode_manager.register(
            name=mode,
            func=func,
            input=input,
            save=save,
            document_input=document_input,
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
    def wrapper(self, *args, **kwargs) -> List[Document]:

        def prepare_input(mode_info) -> List[Any]:
            """Prepare and return the list of inputs based on mode config."""
            if not mode_info.input:
                return []
            if callable(mode_info.input):
                return mode_info.input(self)
            if (url := getattr(self.args, "url", None)):
                return [ScrapedDocument.from_document(
                    document=mode_info.document_input(link=url),
                    source=self.__class__.__name__,
                    mode="restaurant_details"
                ).to_dict()]
            return self.read(filename=mode_info.input)

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

            if input_list:
                for data in input_list:
                    doc = self.create_document(obj=data, document=mode_info.document_input)
                    self.logger.debug(f"Processing {doc}")

                    try:
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
            if mode_info.save is not None:
                mode_info.save(self, list(results))

            self.save(
                links=[ScrapedDocument.from_document(document=r, mode=self.mode, source=self.__class__.__name__) for r in results]
            )
            self.close_browser()

            return list(results)

    return wrapper