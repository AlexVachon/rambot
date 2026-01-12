from rambot import Scraper, bind, pipeline
from rambot.scraper import Document


class RestaurantDoc(Document):
    name: str
    address: str
    ratings: float


@pipeline("cities", "listing", "details")
class BasicScraper(Scraper):

    @bind("cities")
    def cities(self):
        self.load_page("https://www.skipthedishes.com/canada-food-delivery")
        
        return [
            Document(link=f"https://www.skipthedishes.com{path}")
            for el in self.html.find_all("//h4/div/a")
            if (path := el.attrs.get("href"))
        ][:3]
        
    @bind("listing")
    def listing(self, city: Document):
        self.load_page(city.link)
        
        return [
            Document(link=f"https://www.skipthedishes.com{path}")
            for el in self.html.find_all("//a[@data-testid='top-resto']")
            if (path := el.attrs.get("href"))
        ][:1]
    
    @bind("details")
    def details(self, listing: Document):
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
    