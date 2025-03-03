### **Description**  

The `Scraper` class is a versatile and configurable web scraping framework designed to automate data extraction from web pages. It provides an intuitive structure for managing different scraping modes, handling browser automation, and logging.  

### **Installation**

pip install rambot

To use this package, download ChromeDriver:
- Windows : Downliad ChromeDriver https://sites.google.com/chromium.org/driver/downloads and add it to PATH.
- macOS/Linux : `brew install chromedriver` or `sudo apt install chromium-chromedriver`

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
  - Implements a centralized error handling system with `ErrorConfig`.  
  - Uses `loguru` for structured logging and debugging.  

- **Built-in Throttling & Delays:**  
  - Introduces randomized delays to mimic human behavior (`wait()` method).  
  - Ensures compliance with website rate limits.  

- **Decorators for Enhanced Functionality:**  
  - `@errors` for structured error handling.  
  - `@no_print` to suppress unwanted output.  
  - `@scrape` to enforce function structure in scraping processes.  

#### **Usage:**  
1. **Initialize Scraper:**  
   ```python
   scraper = Scraper()
   scraper.setup()  # Parses arguments and validates the mode
   ```
2. **Run Scraping Mode:**  
   ```python
   results = scraper.run()  # Executes the mode registered via @bind
   ```
3. **Extract Elements from a Web Page:**  
   ```python
   elements = scraper.find_all("div.article")
   ```
4. **Save Data to a JSON File:**  
   ```python
   scraper.save(results, ModeResult(status="success"))
   ```

This framework is ideal for web automation, data collection, and structured scraping tasks that require flexibility and reliability. 🚀