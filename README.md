# Spanish News Crawler for Academic Research

A Python web scraping system designed to collect news about China and Asia from major Spanish mainstream media outlets, optimized for academic research.

## Features

- **Multi-site support**: Built-in support for 4 major Spanish media:
  - El País (elpais) - Spain's largest daily
  - El Mundo (elmundo) - Second largest digital media
  - ABC (abc) - Historic authoritative newspaper
  - Agencia EFE (efe) - Spanish national news agency

- **Flexible search**:
  - Support for single or multiple keywords
  - Accepts keywords in Spanish or Chinese
  - Filter by custom date range (YYYY-MM-DD)
  - Select specific media sites or crawl all

- **Structured output**:
  - Standardized JSON format matching academic research needs
  - Returns Python dictionary for programmatic access
  - Can export to JSON file for archiving

- **Respectful crawling**:
  - Configurable request delay (default 3 seconds)
  - Automatic retries with exponential backoff
  - Proper browser headers to avoid blocking
  - Graceful error handling - one failure doesn't stop the whole crawl

- **Easy integration**:
  - Pure parameter-based API, no configuration files
  - Can be imported and called directly from Python scripts
  - Full UTF-8 support for Spanish characters (accents, ñ)

## Installation

```bash
git clone https://github.com/Jin-Yun/news_fetch.git
cd news_fetch
pip install -r requirements.txt
```

## Quick Start

### As a Python module (recommended for research)

```python
from news_fetch import SpanishNewsCrawler

# Initialize crawler with your search parameters
crawler = SpanishNewsCrawler(
    keywords="China Asia",  # Space-separated or list: ["China", "Asia"]
    start_date="2025-01-01",
    end_date="2025-03-28",
    media_sites=["elpais", "efe"],  # Omit for all sites
    delay_seconds=3.0
)

# Run the crawl and get structured results
result = crawler.run()

print(f"Found {result['crawl_info']['total_news']} articles")

# Access articles
for article in result['news_data']:
    print(f"{article['title']} - {article['publish_time']} - {article['url']}")

# Save to JSON file
crawler.save_to_json("china_news_2025.json")
```

### Output JSON Structure

```json
{
  "crawl_params": {
    "keywords": ["China", "Asia"],
    "start_date": "2025-01-01",
    "end_date": "2025-03-28",
    "media_sites": ["elpais", "efe"]
  },
  "crawl_info": {
    "total_news": 42,
    "crawl_time_seconds": 128.5,
    "crawl_finished_at": "2026-03-28T10:30:00",
    "status": "success"
  },
  "news_data": [
    {
      "media": "elpais",
      "title": "China refuerza sus lazos económicos con España",
      "subtitle": "El comercio bilateral alcanza niveles históricos",
      "content": "Contenido completo del artículo...",
      "author": "Juan García",
      "publish_time": "2025-01-15",
      "url": "https://elpais.com/internacional/2025-01-15/...",
      "category": "internacional",
      "crawl_time": "2026-03-28T10:30:00"
    }
  ]
}
```

## Available Media Sites

| Identifier | Name | Type |
|------------|------|------|
| `elpais` | El País | Major daily |
| `elmundo` | El Mundo | Digital daily |
| `abc` | ABC | Historic daily |
| `efe` | Agencia EFE | News agency |

List available sites programmatically:
```python
print(SpanishNewsCrawler.available_media_sites())
# ['elpais', 'elmundo', 'abc', 'efe']
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```
news_fetch/
├── news_fetch/
│   ├── __init__.py
│   ├── crawlers/
│   │   ├── base_crawler.py      # Abstract base class
│   │   ├── el_pais.py            # El País implementation
│   │   ├── el_mundo.py           # El Mundo implementation
│   │   ├── abc_es.py             # ABC implementation
│   │   └── efe.py                # EFE implementation
│   ├── models/
│   │   └── article.py            # Article data model (Pydantic)
│   ├── utils/
│   │   ├── date_parser.py        # Spanish date parsing
│   │   ├── http_client.py        # Respectful HTTP client
│   │   ├── text_cleaner.py       # HTML/text cleaning
│   │   └── exporters.py           # JSON export
│   └── search/
│       └── search_engine.py      # Main SpanishNewsCrawler
├── tests/                         # Unit tests
├── examples/
│   └── example_search.py          # Usage examples
└── requirements.txt
```

## Adding a New Media Site

1. Create a new crawler class in `news_fetch/crawlers/` that inherits from `BaseCrawler`
2. Implement the `search()` and `extract_article()` abstract methods
3. Add the crawler to `MEDIA_CRAWLERS` mapping in `search_engine.py`
4. Add to the README

## Notes for Academic Use

- This tool is for **academic research only**. Please respect the target websites' terms of service
- Default delay of 3 seconds is set to minimize load on servers. Increase delay for large crawls
- Paywalled articles: For sites with paywalls (like El País), the crawler extracts whatever metadata is available without attempting to bypass the paywall

## License

MIT License - for academic research and non-commercial use.
