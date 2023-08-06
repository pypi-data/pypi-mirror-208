# hypersquirrel

## Usage

Module

```bash
pip install hypersquirrel
```

```python
from hypersquirrel import scrape

for file in scrape("scrape_url"):
    print(file)
```

Standalone

```bash
docker-compose up --build -d
```

```bash
curl --location --request POST 'localhost:5000/scrape' \
  --header 'Content-Type: application/json' \
  --data-raw '{ "url": "scrape_url" }'
```
