from datetime import date

from pydantic import BaseModel, Field, field_validator
from typing import Type, Optional, Callable, Dict, Any
from enum import Enum


class Details(BaseModel):
    pass


class Document(BaseModel):
   link: str
   
   def output(self) -> Dict[str, Any]:
       return self.model_dump()


class Mode(BaseModel):
    name: str = Field(alias="name")
    
    func: Optional[Callable] = Field(None, alias="func")
    input: Optional[str] = Field(None, alias="input")
    document_input: Optional[Type[Document]] = Field(None, alias="document_input")
    
    path: Optional[str] = Field(None, alias="path")
    save_logs: bool = Field(False, alias="save_logs")
    logs_output: Optional[str] = Field(None, alias="logs_output")
    
    @field_validator("logs_output", mode="before")
    @classmethod
    def set_default_logs(cls, v, values):
        path = values.data.get("path", ".")
        
        if v is None:
            
            mode = values.data.get('name')
            today = date.today().strftime("%Y-%m-%d")
            
            return f"{path}/{mode}_{today}.log"
        
        return f"{path}/{v}"


class ScraperModeManager:
    _modes = {}

    @classmethod
    def register(
        cls, 
        name: str, 
        func: Optional[Callable] = None, 
        input: Optional[str] = None, 
        document_input: Optional[Type[Document]]  = None,
        save_logs: bool = False,
        logs_output: Optional[str] = None,
        path: Optional[str] = None
    ):
        if name not in cls._modes:
            cls._modes[name] = Mode(
                name=name,
                func=func, 
                input=input, 
                document_input=document_input, 
                save_logs=save_logs,
                logs_output=logs_output,
                path=path
            )

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