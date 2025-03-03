from pydantic import BaseModel, Field
from typing import Optional, Callable
from enum import Enum


class Listing(BaseModel):
    link: str = Field("", alias="link")
    
    def __str__(self):
        return f'{{"link": "{self.link}"}}'


class Restaurant(BaseModel):
    pass


class ScraperModeManager:
    _modes = {}

    @classmethod
    def register(cls, name: str, func: Optional[Callable] = None, input: Optional[str] = None):
        if name not in cls._modes:
            cls._modes[name] = {'function': None, 'input': None}
        
        if func:
            cls._modes[name]['function'] = func
        if input:
            cls._modes[name]['input'] = input

    @classmethod
    def all(cls):
        """Retourne la liste des modes enregistrés."""
        return list(cls._modes.keys())

    @classmethod
    def validate(cls, mode: str):
        if mode not in cls._modes:
            raise ValueError(f"Mode '{mode}' non reconnu. Modes disponibles: {cls.all()}")

    @classmethod
    def get_mode_info(cls, mode: str) -> dict:
        cls.validate(mode)
        return cls._modes[mode]

    @classmethod
    def get_func(cls, mode: str) -> Optional[Callable]:
        cls.validate(mode)
        mode_info = cls.get_mode_info(mode)
        func = mode_info['function']
        if func is None:
            raise ValueError(f"Aucune fonction associée au mode '{mode}'")
        return func


class ModeStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


class ModeResult(BaseModel):
    status: ModeStatus = Field(ModeStatus.ERROR, alias="status")
    message: Optional[str] = Field(None, alias="message")