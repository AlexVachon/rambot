### **Description**  

Rambot is a versatile and configurable web scraping framework designed to automate data extraction from web pages. It provides an intuitive structure for managing different scraping modes, handling browser automation, and logging.  

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

2. **Initialize Scraper and run a scraping mode:**  
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
        ]
      }
    ]
  }
  ```

4. **Extract elements from a web page:**  
  ```python
  elements = self.find_all("div.article")
  ```

5. **Save data to a JSON file:**  
  ```python
  with open("scraped_data.json", "w") as file:
      json.dump(data, file, indent=4)
  ```

This framework is ideal for web automation, data collection, and structured scraping tasks that require flexibility and reliability. 🚀