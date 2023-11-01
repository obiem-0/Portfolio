<hr/>

# Transfermarkt Scraper

A Python scraper for extracting player details from match URLs on `transfermarkt.co.uk`.

### Features

- Extracts player name, profile link, shirt number, coordinates, game ID, and team name.
- Supports scraping multiple URLs at once.
- Uses BeautifulSoup for HTML parsing.

### Requirements

- Python 3.x
- BeautifulSoup4
- Requests


### Usage

1. Modify the `URLS` list in `scraper.py` to include the URLs you want to scrape.

2. Run the scraper:

```bash
python scraper.py
```

The extracted data will be printed to the console
