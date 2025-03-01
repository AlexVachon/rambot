# botasaurus/utils.py
from functools import wraps
from typing import Callable, Any
import json
from loguru import logger as defaul_logger

logger = defaul_logger

def handle_errors(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            logger.error(f"Erreur dans {func.__name__}: {str(e)}")
            raise
    return wrapper

def read_json_file(filename: str) -> Any:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier '{filename}' n'a pas été trouvé.")
    except json.JSONDecodeError:
        raise ValueError(f"Le fichier '{filename}' contient un JSON invalide.")