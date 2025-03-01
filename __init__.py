import scraper
from loguru import logger as default_logger


scraper.logger = default_logger
scraper.utils.logger = default_logger