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

## **The `@bind` Decorator**

The `@bind` decorator supports **Automatic Dependency Discovery**. It "spots" connections between modes by inspecting your Python type hints, making manual configuration optional for linear workflows.

### **Decorator Arguments**

| Argument | Type | Description |
| --- | --- | --- |
| **`mode`** | `str` | **Required.** The CLI name (e.g., `--mode listing`). This also defines the output filename: `listing.json`. |
| **`input`** | `[str \| Callable]` | **Optional.** Manual override. Can be a filename (`"cities.json"`) or a function to fetch data. |
| **`document_output`** | `Type[Document]` | **Optional.** The class used to save results. Automatically detected from return type hints (e.g., `-> list[City]`). |
| **`save`** | `Callable` | **Optional.** A custom function to handle data persistence for this specific mode. |
| **`enable_file_logging`** | `bool` | If `True`, creates a dedicated log file for this mode session. |
| **`log_directory`** | `str` | Directory where mode-specific logs are stored. Defaults to `.`. |

---

## **Usage Options**

### **1. Automatic Discovery (The "Magic" Way)**

Rambot uses an internal type registry to link modes together. If one mode returns a specific `Document` subclass and another mode expects it as an argument, Rambot connects them automatically.

```python
from rambot import Scraper, bind
from rambot.scraper import Document

# Define specific subclasses to act as 'type keys'
class City(Document):
    name: str

class BasicScraper(Scraper):
    @bind("cities")
    def get_cities(self) -> list[City]:
        # Registers: City -> 'cities' mode (outputs cities.json)
        return [City(link="...", name="Vancouver")]

    @bind("listing")
    def get_listings(self, city: City):
        # 'listing' needs 'City', finds 'cities' mode, and loads 'cities.json'
        self.load_page(city.link)
```

### **2. Manual Override (For Generic Documents)**

When multiple modes use the base `Document` class, you must manually specify the input file to avoid collisions.

```python
    @bind("listing", input="cities.json")
    def listing(self, doc: Document) -> list[Document]:
        # Explicitly read from cities.json even if return hints are generic
        ...
```

### **3. Functional Input (Custom Fetching)**

Instead of a file, you can pass a function to `input` to fetch data from a database, API, or external source.

```python
def fetch_from_db(scraper):
    return [{"link": "https://example.com/1"}, {"link": "https://example.com/2"}]

class DatabaseScraper(Scraper):
    @bind("process", input=fetch_from_db)
    def process_data(self, doc: Document):
        self.load_page(doc.link)
```

---

## **Execution Logic & Priority**

When a mode is launched via the CLI, Rambot determines the input data using this hierarchy:

1. **CLI Override**: `--url <link>` ignores all other inputs and processes that single URL.
2. **Manual Input**: If `input` is defined in `@bind` (file or function), it is used next.
3. **Auto-Detection**: Rambot searches the Type Registry for a mode producing the class in the method signature (e.g., `city: City`).
4. **Empty Start**: If no input is found, the mode runs once with no positional arguments.

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
    @bind(mode="details", input="listing", document_output=ProductDoc)
    def details(self, doc) -> ProductDoc:
        self.load_page(doc.link)
        
        # Filter for API/Fetch calls only
        api_calls = self.interceptor.requests(lambda r: r.is_fetch)
        
        # Check for specific API errors
        errors = self.interceptor.requests(lambda r: r.response.is_error)
        
        doc.api_count = len(api_calls)
        return doc
```

## **Pro-Tips**

* **Filtering**: Use `lambda r: r.resource_type == "image"` to find specific assets.
* **Status Handling**: Use `req.response.ok` to verify capture success.
* **DotDict**: All captured requests inherit from `dict`, allowing `json.dump(requests, f)` with no extra code.

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
                "--url", "https://example.com/target"
            ]
        }
    ]
}
```

# **HTTP Request Module**

The `rambot.http` module provides a high-performance, standalone HTTP client for high-speed scraping without a browser. It is built on top of `botasaurus` and `requests`, offering automated retries, advanced header normalization, and seamless integration with browser-like configurations.

---

## **Core Features**

* **Automated Retries**: Built-in exponential backoff and retry logic via `max_retry` and `retry_wait` parameters.
* **Browser Impersonation**: Easily simulate specific browsers (e.g., Chrome) and operating systems (e.g., Windows).
* **Advanced Header Handling**: Automatically normalizes headers to match browser behaviors.
* **Response Parsing**: Automatically parses responses into structured `ResponseContent` or returns raw objects.
* **Error Management**: Robust exception handling for network failures, unsupported methods, and invalid configurations.

---

## **Usage Example**

For rapid data extraction when a full browser session is not required:

```python
from rambot.http import request
from rambot import Scraper, bind
from rambot.scraper import Document

class BasicDoc(Document):
    custom_data: dict

class BasicScraper(Scraper):
    def open_browser(self):
        # Prevents browser from opening for specific mode
        if self.mode == "basic":
            return
        super().open_browser()

    @bind("basic")
    def get_basic(self) -> BasicDoc:
        json_data = requests.request("GET", "https://api.example.com/details", max_retry=3, parsed=True)
        return BasicDoc(link="...", custom_data=json_data)
```

---

## **Function Signature: `request()`**

| Argument | Type | Description | Default |
| --- | --- | --- | --- |
| **`method`** | `Literal["GET", "POST"]` | HTTP verb to use | *Required* |
| **`url`** | `HttpUrl` | The target destination URL. | *Required* |
| **`options`** | `Union[Dict[str, Any], BeautifulSoup, str, Response]` | Dictionary containing headers, proxies, data, or browser settings. | `{}` |
| **`max_retry`** | `int` | Maximum number of attempts in case of failure. | `5` |
| **`retry_wait`** | `int` | Delay in seconds between retry attempts. | `5` |
| **`parsed`** | `bool` | If `False`, returns the raw response instead of a parsed object. | `False` |

---

## **Error Handling**

The module raises specific exceptions to help you debug scraping issues:

* **`MethodError`**: Raised if an unsupported HTTP method is provided.
* **`RequestFailure`**: Raised when the request fails due to network issues or status errors.
* **`OptionsError`**: Raised if the provided `options` dictionary contains invalid types or configurations.
