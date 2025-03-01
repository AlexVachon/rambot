from pydantic import BaseModel, Field

class Listing(BaseModel):
    link: str = Field("", alias="link")
    
    def __str__(self):
        return f'{{"link": "{self.link}"}}'


class Restaurant(BaseModel):
    pass