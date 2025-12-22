# Huispedia Scraper

A Python scraper for extracting property listings from [huispedia.nl](https://www.huispedia.nl/), the Dutch property platform with comprehensive housing data.

## Features

- Scrape property listings across the Netherlands
- Support for multiple Dutch cities (Amsterdam, Rotterdam, Utrecht, etc.)
- Filter by property type (apartment, house)
- Parallel detail page fetching for faster scraping
- Export to CSV format
- Comprehensive property data extraction (40+ fields)
- Value comparison data (Onder/Binnen/Boven de waarde)

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration

### Getting a ScrapingAnt API Key

This scraper uses the [ScrapingAnt API](https://scrapingant.com/) for reliable web scraping with JavaScript rendering.

1. Sign up for a free account at [https://app.scrapingant.com/signup](https://app.scrapingant.com/signup)
2. Get your API key from the dashboard
3. The free tier includes 10,000 API credits

### Setting the API Key

Set your ScrapingAnt API key as an environment variable:

```bash
export SCRAPINGANT_API_KEY="your_api_key_here"
```

Or pass it directly via command line:

```bash
python main.py --api-key "your_api_key_here" --location amsterdam
```

## Usage

### Basic Usage

```bash
# Scrape properties in Amsterdam
python main.py --location amsterdam

# Scrape only apartments in Rotterdam
python main.py --location rotterdam --property apartment

# Scrape houses in Utrecht
python main.py --location utrecht --property house
```

### Advanced Options

```bash
# Limit to first 2 pages
python main.py --location amsterdam --max-pages 2

# Limit to 50 properties
python main.py --location amsterdam --limit 50

# Skip detail pages (faster, less data)
python main.py --location amsterdam --no-details

# Custom output file
python main.py --location amsterdam --output amsterdam_properties.csv

# Increase parallel workers
python main.py --location amsterdam --max-workers 10

# Verbose logging
python main.py --location amsterdam -v
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--location` | `-l` | City to search (default: amsterdam) |
| `--property` | `-p` | Property type: all, apartment, house (default: all) |
| `--output` | `-o` | Output CSV file path (default: properties.csv) |
| `--limit` | | Maximum number of properties to scrape |
| `--max-pages` | | Maximum number of listing pages to scrape |
| `--max-workers` | `-w` | Maximum parallel requests (default: 5) |
| `--no-details` | | Skip fetching detail pages |
| `--api-key` | `-k` | ScrapingAnt API key |
| `--verbose` | `-v` | Enable verbose logging |

## Supported Cities

- Amsterdam
- Rotterdam
- Den Haag (The Hague)
- Utrecht
- Eindhoven
- Groningen
- Tilburg
- Almere
- Breda
- Nijmegen
- Haarlem
- Arnhem
- Enschede
- Amersfoort
- Maastricht
- Leiden
- Delft
- And more...

## Output Fields

| Field | Description |
|-------|-------------|
| url | Property listing URL |
| listing_id | Unique listing identifier |
| title | Property title |
| street_address | Street address |
| postal_code | Dutch postal code |
| city | City name |
| province | Province name |
| price | Property price in EUR |
| price_per_sqm | Price per square meter |
| price_type | Price type (k.k. or v.o.n.) |
| value_comparison | Value assessment (Onder/Binnen/Boven de waarde) |
| living_area | Living area in m² |
| plot_size | Plot size in m² |
| volume | Building volume in m³ |
| rooms | Total number of rooms |
| bedrooms | Number of bedrooms |
| bathrooms | Number of bathrooms |
| floors | Number of floors |
| property_type | Type (Eengezinswoning, Appartement, etc.) |
| house_type | Specific house type (Hoekwoning, Tussenwoning, etc.) |
| build_type | New/Existing building |
| year_built | Construction year |
| renovation_year | Renovation year |
| energy_label | Energy label (A-G) |
| insulation | Insulation types |
| heating | Heating type |
| cv_year | CV boiler installation year |
| roof_type | Roof type |
| kitchen_type | Kitchen type |
| kitchen_amenities | Kitchen amenities list |
| bathroom_amenities | Bathroom amenities list |
| location_type | Location characteristics |
| parking_type | Parking type |
| maintenance_inside | Interior condition |
| maintenance_outside | Exterior condition |
| status | Listing status |
| listed_since | Days on market |
| acceptance | Acceptance terms |
| cadastral_info | Cadastral information |
| description | Property description |
| agent_name | Real estate agent name |
| agent_url | Agent profile URL |
| date_scraped | Scraping timestamp |

## Project Structure

```
HuispediaScraper/
├── main.py           # CLI entry point
├── scraper.py        # Main scraper class
├── models.py         # Property data model
├── utils.py          # Parsing utilities
├── config.py         # Configuration constants
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

## Requirements

- Python 3.8+
- ScrapingAnt API key

## License

MIT License
