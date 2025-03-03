from pydantic import BaseModel, Field
from typing import Type, Optional, Callable
from enum import Enum


class Details(BaseModel):
    pass


class Document():
    def __init__(self, link: str):
        self.link = link
    
    def output(self):
        return {"link": self.link}


class Mode(BaseModel):
    func: Optional[Callable] = Field(None, alias="func")
    input: Optional[str] = Field(None, alias="input")
    document_input: Optional[Type[Document]] = Field(None, alias="document_input")
    document_output: Type[Document] = Field(alias="document_output")


class ScraperModeManager:
    _modes = {}


    @classmethod
    def register(
        cls, 
        name: str, 
        func: Optional[Callable] = None, 
        input: Optional[str] = None, 
        document_output: Optional[Type[Document]] = None, 
        document_input: Optional[Type[Document]]  = None
    ):
        if name not in cls._modes:
            cls._modes[name] = Mode(func=func, input=input, document_input=document_input, document_output=document_output)

    @classmethod
    def all(cls):
        """Retourne la liste des modes enregistrés."""
        return list(cls._modes.keys())

    @classmethod
    def validate(cls, mode: str):
        if mode not in cls._modes:
            raise ValueError(f"Mode '{mode}' non reconnu. Modes disponibles: {cls.all()}")

    @classmethod
    def get_mode(cls, mode: str) -> Mode:
        cls.validate(mode)
        return cls._modes[mode]

    @classmethod
    def get_func(cls, mode: str) -> Optional[Callable]:
        cls.validate(mode)
        mode_info = cls.get_mode(mode)
        func = mode_info.func
        if func is None:
            raise ValueError(f"Aucune fonction associée au mode '{mode}'")
        return func


class ModeStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"


class ModeResult(BaseModel):
    status: ModeStatus = Field(ModeStatus.ERROR, alias="status")
    message: Optional[str] = Field(None, alias="message")