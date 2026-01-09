# **Rambot: Versatile Web Scraping Framework**

## **Description**

Rambot is a versatile and configurable web scraping framework designed to automate data extraction from web pages. It provides an intuitive structure for:

* **Mode Management**: Orchestrate complex scraping workflows via a robust mode manager.
* **Browser Automation**: High-level control of **ChromeDriver** via `botasaurus`.
* **Network Interception**: Native integration with `mitmproxy` to capture and filter background XHR/Fetch requests.
* **Structured Data**: Built-in Pydantic-based `Document` models for reliable data persistence.
* **Advanced HTTP**: A standalone request module for high-speed scraping without a browser.

---

## **Installation**

```bash
pip install --upgrade rambot
```

### **ChromeDriver Dependency**

Rambot requires `ChromeDriver`. Install it based on your OS:

* **macOS**: `brew install chromedriver`
* **Linux**: `sudo apt install chromium-chromedriver`
* **Windows**: Download from the [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/) page.

---

## **Key Features**

### **1. Network Interception & Filtering**

Capture real-time network traffic using the integrated `mitmproxy` backend.

* **Auto-categorization**: Requests are typed as `fetch`, `document`, `script`, `stylesheet`, `image`, `font`, or `manifest`.
* **Dot Notation**: Access data cleanly: `req.response.status`, `req.url`, `req.is_fetch`.
* **Zero-Config Export**: Directly serializable with `json.dump(self.interceptor.requests(), f)`.

### **2. Chained Execution Pipeline**

Connect different scraping phases (e.g., Search -> Details -> Download) using the `@bind` decorator. Rambot automatically handles input/output JSON files between modes.

### **3. Optimized Performance**

* **Resource Management**: Easily toggle browser usage per mode to save CPU/RAM.
* **Throttling**: Randomized `wait()` delays to mimic human behavior and avoid detection.

---

## **Basic Scraper Example**

```python
from rambot import Scraper, bind
from rambot.scraper import Document

class BasicScraper(Scraper):
    BASE_URL: str = "https://www.example.com"

    @bind(mode="listing")
    def available_items(self) -> list[Document]:
        self.get(f"{self.BASE_URL}/catalog")
        links = self.find_all(".item-link")
        
        return [
            Document(link=self.BASE_URL + el.get_attribute("href"))
            for el in links
        ]

if __name__ == "__main__":
    app = BasicScraper()
    app.run()
```

---

## **Advanced Usage: Network Interceptor**

Capture background API traffic while navigating. This is ideal for sites like **SkipTheDishes** that load menus via background JSON calls.

```python
from pydantic import Field
from rambot import Scraper, bind
from rambot.scraper import Document

class ProductDoc(Document):
    price: float = Field(0.0)
    api_count: int = Field(0)

class InterceptorScraper(Scraper):
    @bind(mode="details", input="listing", document_input=ProductDoc)
    def details(self, doc) -> ProductDoc:
        self.load_page(doc.link)
        
        # Filter for API/Fetch calls only
        # This catches modern Fetch API calls even without XHR headers
        api_calls = self.interceptor.requests(lambda r: r.is_fetch)
        
        # Check for specific API errors
        errors = self.interceptor.requests(lambda r: r.response.is_error)
        
        doc.api_count = len(api_calls)
        return doc
```

---

## **The `@bind` Decorator**

| Argument | Type | Description |
| --- | --- | --- |
| **`mode`** | `str` | **Required.** The CLI name (e.g., `--mode details`). |
| **`input`** | `str` | Name of the JSON file to read input from. |
| **`document_input`** | `Type[Document]` | The Pydantic model used to parse input items. |
| **`log_directory`** | `str` | Custom path for mode-specific logs. |

---

## **Configuration**

### **VS Code Launch Setup**

Use `.vscode/launch.json` to debug specific modes and URLs:

```json
{
    "configurations": [
        {
            "name": "Scrape Details",
            "type": "python",
            "request": "launch",
            "program": "main.py",
            "args": [
                "--mode", "details",
                
                // NOTE: --url will override input in @bind
                "--url", "https://example.com/target"
            ]
        }
    ]
}
```

### **HTTP Request Module**

For high-speed scraping without a browser:

```python
from rambot.http import requests

# Automated retries and case-insensitive header handling
response = requests.request("GET", "https://api.example.com", max_retry=3)
data = response.json()
```

---

## **Pro-Tips**

* **Filtering**: Use `lambda r: r.resource_type == "image"` to find specific assets.
* **Status Handling**: Use `req.response.ok` to verify capture success.
* **DotDict**: All captured requests inherit from `dict`, allowing `json.dump(requests, f)` with no extra code.
