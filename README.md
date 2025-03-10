# **Rambot: Versatile Web Scraping Framework**  



## **Description**    
Rambot is a versatile and configurable web scraping framework designed to automate data extraction from web pages. It provides an intuitive structure for:  
- Managing different scraping modes.  
- Automating browser navigation.  
- Handling logs and errors.  
- Performing advanced HTTP requests to interact with APIs.  



## **Installation**    
```bash
pip install --upgrade rambot
```

### **ChromeDriver Dependency**  
Rambot uses `ChromeDriver` for automated browsing. Install it based on your operating system:  
- **Windows**: [Download ChromeDriver here](https://sites.google.com/chromium.org/driver/downloads) and add it to your `PATH`.
- **macOS**: Install via Homebrew:  
  ```bash
  brew install chromedriver
  ```
- **Linux**: Install via APT:  
  ```bash
  sudo apt install chromium-chromedriver
  ```



## **Key Features**    
### **1. Mode-Based Execution**  
- Supports multiple scraping modes via `ScraperModeManager`.
- Use `@bind` decorator or `self.mode_manager.register()` to associate functions with specific modes.

### **2. Headless Browser Control**  
- Integrates with `botasaurus` for automation.
- Advanced proxy management, image blocking, and extension loading.
- Uses `ChromeDriver` to navigate and extract content.

### **3. Optimized Data Handling**  
- Saves extracted data in JSON format.
- Reads and processes existing data files as input.
- Models structured data using `Document`.

### **4. Error Management & Logging**  
- Centralized error handling with `ExceptionHandler`.
- Uses `loguru` for detailed and structured logging.

### **5. Scraping Throttling & Delays**  
- Introduces randomized delays to mimic human behavior (`wait()`).
- Ensures compliance with website rate limits.

### **6. Useful Decorators**
- `@no_print`: Suppresses unwanted output.
- `@scrape`: Enforces function structure in scraping processes.



## **Basic Usage**    

### **1. Create a Scraper**  
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

if __name__ == "__main__":
    app = App()
    app.run()  # Executes the mode registered in launch.json
```

### **2. Configure `launch.json` in VSCode**  
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
      "args": ["--mode", "cities"]
    }
  ]
}
```

### **3. Retrieve Results**  
Extracted data is saved in `{mode}.json`:  
```json
{
  "data": [
    {"link": "https://www.skipthedishes.com/cities/calgary"},
    {"link": "https://www.skipthedishes.com/cities/brandon"},
    {"link": "https://www.skipthedishes.com/cities/welland"}
  ],
  "run_stats": {"status": "success", "message": null}
}
```



# **HTTP Request Module**    
## **Description**  
This module allows sending HTTP requests with automatic error handling, logging, and retry attempts.

## **Example Usage**  
```python
from rambot.http import requests

response = requests.request(
    method="GET",
    url="http://example.com",
    options={"headers": {"User-Agent": "CustomAgent"}, "timeout": 10},
    max_retry=3,
    retry_wait=2
)
```

## **Using Proxies and Custom Headers**  
```python
response = requests.request(
    method="POST",
    url="http://example.com/api",
    options={
        "proxies": {"http": "http://my-proxy.com:{port}", "https": "http://my-proxy.com:{port}"},
        "json": {"key": "value"},
        "headers": {"Authorization": "Bearer TOKEN"}
    },
    max_retry=5,
    retry_wait=3
)
```

## **Usage in a Scraper**  
```python
from rambot.http import requests
from rambot.scraper import Scraper, bind
from rambot.models import Document
import typing

class App(Scraper):
    def open(self, wait=True):
        if self.mode in ["cities"]:
            return  # Prevents browser from opening for this mode
        return super().open(wait)

    @bind(mode="cities")
    def cities(self) -> typing.List[Document]:
        response = requests.request(
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

## **Advantages**  
- **Scraping without a browser**: Reduces resource consumption.
- **Retry mechanism**: Minimizes failures.
- **Fast data extraction**: Parses HTML directly with `requests`.

With Rambot, automate and optimize your data extractions efficiently! 🚀
