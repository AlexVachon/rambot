# **Description**  

Rambot is a versatile and configurable web scraping framework designed to automate data extraction from web pages. 

It provides an intuitive structure for managing different scraping modes, handling browser automation, and logging. It also includes a powerful HTTP request handling function enhancing Rambot’s capabilities for web scraping and data retrieval from APIs.  



# **Installation**

`pip install rambot`

To use this package, download ChromeDriver:
- **Windows:** Download ChromeDriver from [here](https://sites.google.com/chromium.org/driver/downloads) and add it to PATH.
- **macOS/Linux:** Install using:
  - `brew install chromedriver` (for macOS)
  - `sudo apt install chromium-chromedriver` (for Linux)


## **Key Features:**  

- **Mode-based Execution:**  
  - Supports multiple scraping modes, validated through `ScraperModeManager`.  
  - Uses the `@bind` decorator or `self.mode_manager.register()` to register functions for specific modes 

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


# **Basic Usage:**

1. **Create your scraper using the `Scraper` class:**
  ```python
from rambot.scraper import Scraper, bind
from rambot.scraper.models import Document

import typing

class App(Scraper):

    BASE_URL: str = "https://www.skipthedishes.com"

    @bind(mode="cities")
    def available_cities(self) -> typing.List[Document]:
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
    app = App()
    app.run() # Executes the mode registered via launch.json file
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
4. **Find results in `{mode}.json` file"**
 ```json
 {
    "data": [
        {
            "link": "https://www.skipthedishes.com/cities/calgary"
        },
        {
            "link": "https://www.skipthedishes.com/cities/brandon"
        },
        {
            "link": "https://www.skipthedishes.com/cities/welland"
        }
    ],
    "run_stats": {
        "status": "success",
        "message": null
    }
  }
 ```

# **Using requests:**  

In some cases, you may want to prevent the browser from opening and instead use the `requests` module for making HTTP requests. Rambot allows you to specify modes where browser automation is disabled, and requests are used instead.  

#### **Example: Fetching Cities Without Opening a Browser**  

```python
from rambot.requests import requests
from rambot.scraper import Scraper, bind
from rambot.models import Document

import typing

class App(Scraper):

    def open(self, wait=True):
        if self.mode in ["cities"]:
            return  # Prevent browser from opening for this mode
        return super().open(wait)

    @bind(mode="cities")
    def cities(self) -> typing.List[Document]:
        response = requests.send(
            method="GET",
            url="https://www.skipthedishes.com/canada-food-delivery",
            options={"timeout": 15},
            max_retry=5,
            retry_wait=1.25
        )
        elements = response.select("h4 div a")
        
        return [
            Document(link=self.BASE_URL + href)
            for element in elements
            if (href := element.get("href"))
        ]
```

#### **Key Features:**  
- **Disabling Browser for Specific Modes**: The `open` method is overridden to prevent opening the browser for the `"cities"` mode.  
- **Making HTTP Requests**: The `requests.send()` method is used to fetch data from a webpage.  
- **Retry Mechanism**: Supports retrying failed requests with customizable `max_retry` and `retry_wait` parameters.  
- **Extracting Links**: The response is parsed to extract relevant links.  

This approach provides a more lightweight and efficient alternative when full browser automation is unnecessary. 🚀

