## WebWatchDog
A Python library to check if a website is up or down.

### Installation
pip install webwatchdog

### Usage
```python
from webwatchdog import up_or_down

url = "https://example.com"
status, message = up_or_down.check_website(url)

if status:
    print("✓", message)
else:
    print("✗", message)
```

