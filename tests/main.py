from rambot import Scraper, bind
from rambot.scraper import Document

import json

class Restaurant(Document):
    name: str
    address: str
    ratings: float


class BasicScraper(Scraper):
    
    @bind("details", enable_file_logging=False)
    def details(self, doc: Document) -> Restaurant:
        link = doc.link
        self.load_page(link)
           
        name = self.name()
        address = self.address()
        ratings = self.ratings()
        
        self.sleep(10)
        
        reqs = self.interceptor.requests(lambda r: r.resource_type not in ["image", "font", "stylesheet"])
        main_doc = self.interceptor.requests(lambda r: r.resource_type == "document")
        api_traffic = self.interceptor.requests(lambda r: r.resource_type == "fetch")
        
        return Restaurant(
            link=link,
            name=name,
            address=address,
            ratings=ratings
        )
        
        
    def name(self) -> str:
        name = self.html.find("//h1", first=True).text.strip()
        self.logger.debug(f"Name: {name}")
        
        return name
    
    
    def address(self) -> str:
        location = self.html.find(f"//div[@data-testid='partner-metadata-wrapper']/div/span", first=True).text.strip()
        self.logger.debug(f"Address: {location}")
        
        return location


    def ratings(self) -> float:
        ratings = self.html.find("//span[@aria-label='Skip Score']", first=True).text.strip()
        self.logger.debug(f"Ratings: {ratings}")
        
        return float(ratings)


if __name__ == "__main__":
    app = BasicScraper()
    app.run()
    