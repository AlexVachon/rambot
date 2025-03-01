# tests/test_config.py
import pytest
from botasaurus.config import ScraperConfig

def test_config_validation():
    config = ScraperConfig(headless=True, window_size=1920)
    assert config.headless == True
    assert config.window_size == 1920

def test_config_invalid_window_size():
    with pytest.raises(ValueError):
        ScraperConfig(window_size=-1)