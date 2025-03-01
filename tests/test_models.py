# tests/test_models.py
import pytest
from botasaurus.models import Listing

def test_listing_validation():
    listing = Listing(link="https://example.com")
    assert listing.link == "https://example.com"
    assert listing.listing_data == {}