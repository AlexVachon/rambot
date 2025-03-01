# botasaurus/exceptions.py
class DriverError(Exception):
    """Base exception class for driver-related errors"""
    pass

class ScrapingError(Exception):
    """Base exception class for scraping-related errors"""
    pass