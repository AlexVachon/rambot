from rambot import Scraper, bind
from rambot.scraper import Document


class Restaurant(Document):
    name: str
    address: str
    reviews: int

class City(Document):
    name: str
    province: str

class BasicScraper(Scraper):
    
    def setup(self):
        self.update_driver_config(headless=True)
        return super().setup()
    
    @bind("cities")
    def cities(self) -> list[City]:
        self.load_page("https://www.skipthedishes.com/canada-food-delivery")
        
        results = []
        
        for province_el in self.html.find_all("//h3"):
            province = province_el.text.strip()
            
            city_links = self.html.find_all(
                "./following-sibling::div[1]//h4/div/a", 
                root=province_el
            )
            
            for link_el in city_links:
                path = link_el.attrs.get("href")
                city_name = link_el.text.strip()
                
                results.append(
                    City(
                        link=f"https://www.skipthedishes.com{path}",
                        name=city_name,
                        province=province
                    )
                )
                
                if len(results) >= 3:
                    return results
        
        return results
        
    @bind("listing", input="cities.json", document_input=City)
    def listing(self, city: City) -> list[Document]:
        self.load_page(city.link)
        
        return [
            Document(link=f"https://www.skipthedishes.com{path}")
            for el in self.html.find_all("//a[@data-testid='top-resto']")
            if (path := el.attrs.get("href"))
        ][:3]
    
    @bind("details", input="listing.json")
    def details(self, listing: Document) -> Restaurant:
        self.load_page(listing.link)
        
        name = self.html.find("//h1").text.strip()
        address = self.get_address()
        reviews = self.get_reviews()
        
        return Restaurant(
            name=name,
            address=address,
            reviews=reviews,
            link=listing.link
        )
        
    def get_address(self) -> str:
        els = self.html.find_all('//div[@data-testid="partner-metadata-wrapper"]/div/span')
        
        address = ", ".join([el.text.strip() for el in els])
        
        return address
    
    def get_reviews(self) -> float:
        el = self.html.find("//span[@aria-label='Skip Score']")
        return int(el.text.strip())
    
    
if __name__ == "__main__":
    app = BasicScraper()
    app.run()
    