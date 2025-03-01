from pydantic import model_validator
from pydantic_settings import BaseSettings


from typing import Optional, List
from typing_extensions import Self

class ScraperConfig(BaseSettings):
    class Config:
        env_prefix = "SCRAPER_"
        env_nested_delimiter = "__"
        env_file = ".env"
        env_file_encoding = "utf-8"
        
    # Configuration de base
    headless: bool = False
    proxy: Optional[str] = None
    profile: Optional[str] = None
    tiny_profile: bool = False
    block_images: bool = True
    block_images_and_css: bool = False
    wait_for_complete_page_load: bool = True
    rotate_user_agent: bool = True
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3"
    beep: bool = False
    
    # Configuration des fenêtres
    window_size: int = 1920
    
    # Configuration des délais
    min_delay: int = 2
    max_delay: int = 5
    
    # Configuration du langage
    lang: str = "en"
    
    # Configuration des extensions
    extensions: List[str] = []
    arguments: List[str] = [
        "--ignore-certificate-errors",
        "--disable-blink-features=AutomationControlled",
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3",
        "--disable-extensions",
        "--disable-popup-blocking",
        "--profile-directory=Profile 1",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding",
        "--enable-features=NetworkService,NetworkServiceInProcess",
        "--disable-features=site-isolation-trials"
    ]
    
    # Validation des délais
    @model_validator(mode="after")
    def check_delays(self) -> Self:
        min_delay = self.min_delay
        max_delay = self.max_delay
        if min_delay is not None and max_delay is not None and min_delay > max_delay:
            raise ValueError("min_delay cannot be greater than max_delay")
        return self
    
    # Validation de la taille de fenêtre
    @model_validator(mode="after")
    def check_window_size(self) -> Self:
        window_size = self.window_size
        if window_size is not None and window_size < 640:
            raise ValueError("Window size must be at least 640 pixels")
        return self
    
    # Validation du langage
    @model_validator(mode="after")
    def check_language(self) -> Self:
        lang = self.lang
        if lang is not None and not lang.isalpha():
            raise ValueError("Language code must contain only letters")
        return self