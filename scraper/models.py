# botasaurus/models.py
from pydantic import BaseModel, Field
from typing import Dict, Any

class Listing(BaseModel):
    link: str = Field("", alias="link")
    listing_data: Dict[str, Any]