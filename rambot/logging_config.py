from loguru import logger
import sys

logger.remove()

current_format = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> - <red>{class_name}</red> - <level>{level}</level> - <white>{message}</white>"


def get_logger(name: str):
    return logger.bind(module=name)


def update_logger_config(
    class_name: str = "Scraper",
    log_to_file: bool = False,
    file_path: str = "app.log"
):
    """
    Updates the logger configuration by dynamically inserting the class name.
    """
    global current_format

    format_str = current_format.replace("{class_name}", class_name)

    logger.remove()

    logger.add(sys.stdout, format=format_str, colorize=True)

    if log_to_file:
        logger.add(file_path, format=format_str, colorize=False)


def set_logger_format(format: str):
    """
    Dynamically updates the logger format.
    """
    update_logger_config(format=format)
