import typing


class ScraperConfig:
    """
    Configuration class for the scraper.

    This class holds various configuration options for a web scraper, including settings for error handling,
    browser options, and performance tuning.

    Attributes:
        headless (bool): Whether to run the browser in headless mode (without a GUI).
        proxy (str, optional): The proxy URL to use for the scraper, if any.
        profile (str, optional): The profile to use for the browser session, if any.
        tiny_profile (bool): Whether to use a minimal browser profile to optimize speed and resource usage.
        block_images (bool): Whether to block loading images in the browser for faster scraping.
        block_images_and_css (bool): Whether to block both images and CSS for maximum speed.
        wait_for_complete_page_load (bool): Whether to wait for the entire page to load before scraping.
        extensions (List[str]): A list of browser extension paths to load during the scraping process.
        arguments (List[str]): A list of command-line arguments to pass to the browser.
        user_agent (str, optional): The custom user agent string to use for requests.
        lang (str, optional): The language setting for the scraper.
        beep (bool): Whether to play a beep sound when the scraping is complete or encounters an error.
    """
    def __init__(
        self,
        headless: bool = False,
        proxy: str = None,
        profile: str = None,
        tiny_profile: bool = False,
        block_images: bool = False,
        block_images_and_css: bool = False,
        wait_for_complete_page_load: bool = False,
        extensions: typing.List[str] = [],
        arguments: typing.List[str] = [],
        user_agent: str = None,
        lang: str = None,
        beep: bool = False,
    ):
        """
        Initializes the ScraperConfig object with the specified configuration options.

        Args:
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
            proxy (str, optional): The proxy URL to use for the scraper. Defaults to None.
            profile (str, optional): The profile to use for the browser session. Defaults to None.
            tiny_profile (bool, optional): Whether to use a minimal browser profile. Defaults to False.
            block_images (bool, optional): Whether to block images in the browser. Defaults to False.
            block_images_and_css (bool, optional): Whether to block both images and CSS. Defaults to False.
            wait_for_complete_page_load (bool, optional): Whether to wait for the page to load completely.
                Defaults to False.
            extensions (List[str], optional): A list of browser extension paths to load. Defaults to an empty list.
            arguments (List[str], optional): A list of command-line arguments for the browser. Defaults to an empty list.
            user_agent (str, optional): A custom user agent string for the scraper. Defaults to None.
            lang (str, optional): The language setting for the scraper. Defaults to None.
            beep (bool, optional): Whether to play a beep sound when the scraping process is complete. Defaults to False.
        """
        
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
