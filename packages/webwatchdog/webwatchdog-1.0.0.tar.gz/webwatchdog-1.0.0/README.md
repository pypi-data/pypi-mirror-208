## Up or Down
A Python library to check if a website is up or down.

### Installation
pip install up_or_down

### Usage
```python
from website_checker import checker

url = "https://example.com"
status, message = checker.check_website(url)

if status:
    print("✓", message)
else:
    print("✗", message)
```

