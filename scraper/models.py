from pydantic import BaseModel, Field
from typing import Literal

class Listing(BaseModel):
    link: str = Field("", alias="link")
    
    def __str__(self):
        return f'{{"link": "{self.link}"}}'

class Restaurant(BaseModel):
    pass


class ScraperModeManager:
    _modes = {}

    @classmethod
    def add_mode(cls, name: str):
        """Ajoute un nouveau mode si non existant."""
        if name not in cls._modes:
            cls._modes[name] = name

    @classmethod
    def get_modes(cls):
        """Retourne tous les modes disponibles."""
        return list(cls._modes.keys())

    @classmethod
    def validate_mode(cls, mode: str):
        """Vérifie si le mode existe, sinon lève une erreur."""
        if mode not in cls._modes:
            raise ValueError(f"Mode '{mode}' non reconnu. Modes disponibles: {cls.get_modes()}")