from typing import Type, List, Callable
from typing_extensions import TypedDict


class ErrorConfig(TypedDict, total=True):
    must_raise: Callable[[Type[Exception]], bool]
    create_logs: Callable[[Type[Exception]], bool]


class ScraperConfig:
    def __init__(
        self,
        must_raise: List[Type[Exception]] = [Exception],
        create_error_logs: bool = False,
        headless: bool = False,
        proxy: str = None,
        profile: str = None,
        tiny_profile: bool = False,
        block_images: bool = False,
        block_images_and_css: bool = False,
        wait_for_complete_page_load: bool = False,
        extensions: List[str] = [],
        arguments: List[str] = [],
        user_agent: str = None,
        lang: str = None,
        beep: bool = False,
    ):
        self.must_raise = must_raise
        self.create_error_logs = create_error_logs
        self.headless = headless
        self.proxy = proxy
        self.profile = profile
        self.tiny_profile = tiny_profile
        self.block_images = block_images
        self.block_images_and_css = block_images_and_css
        self.wait_for_complete_page_load = wait_for_complete_page_load
        self.extensions = extensions
        self.arguments = arguments
        self.user_agent = user_agent
        self.lang = lang
        self.beep = beep
