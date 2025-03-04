from loguru import logger
import sys

logger.remove()


def get_logger(name: str):
    return logger.bind(module=name)


def update_logger_config(
                          format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <red>Scraper</red> - <level>{level}</level> - <white>{message}</white>", 
                          log_to_file=False, 
                          file_path="app.log"):

    if not any(handler.name == 'stdout' for handler in logger._core.handlers):
        logger.add(sys.stdout, format=format, colorize=True)
    
    if log_to_file:
        logger.add(file_path, format=format, colorize=False)
