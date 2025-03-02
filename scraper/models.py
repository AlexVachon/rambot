from pydantic import BaseModel, Field
from typing import Optional
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
    def register(cls, name: str):
        if name not in cls._modes:
            cls._modes[name] = name

    @classmethod
    def all(cls):
        return list(cls._modes.keys())

    @classmethod
    def validate(cls, mode: str):
        if mode not in cls._modes:
            raise ValueError(f"Mode '{mode}' non reconnu. Modes disponibles: {cls.all()}")
        

class ModeStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


class ModeResult(BaseModel):
    status: ModeStatus = Field(ModeStatus.ERROR, alias="status")
    message: Optional[str] = Field(None, alias="message")