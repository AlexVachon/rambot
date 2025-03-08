# botasaurus/utils.py
from typing import Any
import json

def read_json_file(filename: str) -> Any:
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"Le fichier '{filename}' n'a pas été trouvé.")
    except json.JSONDecodeError:
        raise ValueError(f"Le fichier '{filename}' contient un JSON invalide.")