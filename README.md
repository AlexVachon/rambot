### **Description**  

Rambot is a versatile and configurable web scraping framework designed to automate data extraction from web pages. It provides an intuitive structure for managing different scraping modes, handling browser automation, and logging.

This framework is ideal for web automation, data collection, and structured scraping tasks that require flexibility and reliability. 🚀

### **Installation**

`pip install rambot`

To use this package, download ChromeDriver:
- **Windows:** Download ChromeDriver from [here](https://sites.google.com/chromium.org/driver/downloads) and add it to PATH.
- **macOS/Linux:** Install using:
  - `brew install chromedriver` (for macOS)
  - `sudo apt install chromium-chromedriver` (for Linux)

#### **Key Features:**  
- **Mode-based Execution:**  
  - Supports multiple scraping modes, validated through `ScraperModeManager`.  
  - Uses the `@bind` decorator to register functions for specific modes.  

- **Headless Browser Control:**  
  - Integrates with `botasaurus` for browser automation.  
  - Provides options for handling proxies, blocking images, and loading extensions.  
  - Uses `ChromeDriver` to navigate and extract content from websites.  

- **Efficient Data Handling:**  
  - Saves scraped data in JSON format.  
  - Reads and processes existing data files for input.  
  - Supports structured data representation using the `Document` model.  

- **Error Management & Logging:**  
  - Implements a centralized error-handling system with `ErrorConfig`.  
  - Uses `loguru` for structured logging and debugging.  

- **Built-in Throttling & Delays:**  
  - Introduces randomized delays to mimic human behavior (`wait()` method).  
  - Ensures compliance with website rate limits.  

- **Decorators for Enhanced Functionality:**  
  - `@errors` for structured error handling.  
  - `@no_print` to suppress unwanted output.  
  - `@scrape` to enforce function structure in scraping processes.  

#### **Usage:**
1. **Create your scraper using `Scraper`:**
  ```python
  from rambot.scraper import Scraper, bind
  from rambot.scraper.models import Document

  class MyScraper(Scraper):

    @bind(mode="cities")
    def cities(self) -> List[Document]:
        self.get("https://www.skipthedishes.com/canada-food-delivery")
        
        elements = self.find_all("h4 div a")
        
        return [
            Document(link=self.BASE_URL + href)
            for element in elements
            if (href := element.get_attribute("href"))
        ]
  ```

2. **Initialize Scraper and run method:**  
  ```python
  if __name__ == "__main__":
    scraper = Scraper()
    scraper.run() # Executes the mode registered via @bind
  ```

3. **Launch your scraper using `.vscode/launch.json`:**  
  ```json
  {
    "version": "0.2.0",
    "configurations": [
      {
        "name": "cities",
        "type": "python",
        "request": "launch",
        "program": "main.py",
        "justMyCode": false,
        "args": [
            "--mode", "cities"
            // "--url" is not a required arg. It can be used to test your function using the provided link. 
            // It should only be used in modes that require an input.
        ]
      }
    ]
  }
  ```


### **Examples**

The following example demonstrates how to use the `Rambot` framework to scrape data from SkipTheDishes, starting from city listings to restaurant details.

```python
from rambot.scraper import Scraper, bind
from rambot.scraper.models import Document

from typing import List, Optional


class Restaurant(Document):
    name: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None


class App(Scraper):

    BASE_URL: str = "https://www.skipthedishes.com"

    @bind(mode="cities")
    def cities(self) -> List[Document]:
        self.get("https://www.skipthedishes.com/canada-food-delivery")
        
        elements = self.find_all("h4 div a")
        
        return [
            Document(link=self.BASE_URL + href)
            for element in elements 
            if (href := element.get_attribute("href"))
        ]


    @bind(mode="restaurant_links", input="cities.json", document_input=Document)
    def listing(self, listing: Document) -> List[Document]:
        
        url: str = listing.link
        self.get(url)
        
        elements = self.find_all("a[data-testid='top-resto']")
        
        return [
            Document(link=self.BASE_URL + href) 
            for element in elements
            if (href := element.get_attribute("href"))
        ]


    @bind(mode="restaurant_details", input="restaurant_links.json", document_input=Document)
    def restaurant_details(self, listing: Document) -> Restaurant:
        url = listing.link
        
        restaurant = Restaurant(link=url)
            
        self.get(url)

        self.process_details(restaurant=restaurant)
        
        return restaurant


    def process_details(self, restaurant: Restaurant) -> Restaurant:
        restaurant.name = self.get_name()
        restaurant.address = self.get_address()


    def get_name(self) -> str:
        return self.find("div[data-testid='partner-metadata-wrapper'] h1").text


    def get_address(self) -> str:
        elements = self.find_all("div[data-testid='partner-metadata-wrapper'] div span")
        
        address_elements = [element.text for element in elements if len(element.text.split()) > 1]
        
        return ', '.join(address_elements)


if __name__ == "__main__":
    app = App()
    app.run()
```

#### **Modes Workflow**
In this example, the following modes are executed in sequence:
1. **cities**: This mode scrapes the city listings from the main page (`https://www.skipthedishes.com/canada-food-delivery`).
2. **restaurant_links**: Once the city listings are gathered, this mode extracts links to individual restaurant listings.
3. **restaurant_details**: Finally, this mode scrapes detailed information (like name and address) for each restaurant.

Here’s how you can add the section explaining how the returned object from a mode can be changed, and how it works with a custom class that inherits from `Document`:

#### **Returning Custom Objects from Modes**

In `Rambot`, you can return custom objects from modes by creating classes that inherit from `Document`. This allows you to extend the data structure and store more specific information related to your scraping task.

For example, in the following mode, we define a custom `Restaurant` class that inherits from `Document`. The mode `restaurant_details` returns an instance of `Restaurant` instead of the default `Document` class.

```python
class Restaurant(Document):
    name: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = None

@bind(mode="restaurant_details", input="restaurant_links.json", document_input=Document)
def restaurant_details(self, listing: Document) -> Restaurant:
    url = listing.link
    
    # Create an instance of the Restaurant class
    restaurant = Restaurant(link=url)
        
    self.get(url)

    # Process the details to populate the Restaurant object
    self.process_details(restaurant=restaurant)
    
    # Return the Restaurant object
    return restaurant
```

#### **How it Works**
- The `Restaurant` class inherits from `Document`, allowing us to extend the basic document with additional fields like `name`, `address`, and `rating`.
- The mode `restaurant_details` processes the details of a restaurant and returns an instance of the `Restaurant` class instead of a `Document`.
- By returning a custom object, you can easily extend the base functionality of Rambot to suit your needs, enabling more structured data handling and more specific attributes in your scraped data.

This approach only works when the returned object inherits from `Document`, which ensures that it integrates smoothly with the rest of the framework’s features.

This section explains how to customize the returned object in a mode by inheriting from `Document`, using the example of the `Restaurant` class. It shows the flexibility of `Rambot` when working with more specific data structures, making it adaptable to different scraping tasks.

Each mode is chained and relies on the output of the previous mode as its input, ensuring a seamless flow of data extraction.

This structure highlights the step-by-step scraping process, the modes involved, and how they are executed in sequence to gather all necessary data.
