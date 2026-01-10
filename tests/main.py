from rambot import Scraper, bind
from rambot.scraper import Document
from rambot.helpers import By


class RestaurantDoc(Document):
    name: str
    address: str
    ratings: float

class CityDoc(Document):
    pass

class ListingDoc(Document):
    pass

class BasicScraper(Scraper):
    

    @bind("cities")
    def cities(self) -> list[CityDoc]:
        self.load_page("https://www.skipthedishes.com/canada-food-delivery")
        
        return [
            CityDoc(link=f"https://www.skipthedishes.com{path}")
            for el in self.html.find_all("//h4/div/a")
            if (path := el.attrs.get("href"))
        ][:3]
        
    @bind("listing")
    def listing(self, city: CityDoc) -> list[ListingDoc]:
        self.load_page(city.link)
        
        return [
            ListingDoc(link=f"https://www.skipthedishes.com{path}")
            for el in self.html.find_all("//a[@data-testid='top-resto']")
            if (path := el.attrs.get("href"))
        ][:3]
    
    @bind("details")
    def details(self, listing: ListingDoc) -> RestaurantDoc:
        self.load_page(listing.link)
        
        name = self.html.find("//h1").text.strip()
        address = self.get_address()
        reviews = self.get_reviews()
        
        return RestaurantDoc(
            name=name,
            address=address,
            ratings=reviews,
            link=listing.link
        )
        
    def get_address(self) -> str:
        els = self.html.find_all('//div[@data-testid="partner-metadata-wrapper"]/div/span')
        
        address = ", ".join([el.text.strip() for el in els])
        
        return address
    
    def get_reviews(self) -> float:
        el = self.html.find("//span[@aria-label='Skip Score']")
        return float(el.text.strip())
    
    
if __name__ == "__main__":
    app = BasicScraper()
    app.run()
    