"""Configuration settings for Huispedia scraper."""

import os

# ScrapingAnt API configuration
SCRAPINGANT_API_KEY = os.environ.get("SCRAPINGANT_API_KEY", "")
SCRAPINGANT_API_URL = "https://api.scrapingant.com/v2/general"

# Base URLs
BASE_URL = "https://huispedia.nl"
SEARCH_URL = f"{BASE_URL}/koopwoningen"

# Default settings
DEFAULT_MAX_WORKERS = 5
DEFAULT_TIMEOUT = 60

# Supported Dutch cities
LOCATIONS = {
    "amsterdam": "amsterdam",
    "rotterdam": "rotterdam",
    "den-haag": "den-haag",
    "utrecht": "utrecht",
    "eindhoven": "eindhoven",
    "groningen": "groningen",
    "tilburg": "tilburg",
    "almere": "almere",
    "breda": "breda",
    "nijmegen": "nijmegen",
    "haarlem": "haarlem",
    "arnhem": "arnhem",
    "enschede": "enschede",
    "amersfoort": "amersfoort",
    "zaanstad": "zaanstad",
    "apeldoorn": "apeldoorn",
    "hoofddorp": "hoofddorp",
    "maastricht": "maastricht",
    "leiden": "leiden",
    "dordrecht": "dordrecht",
    "zoetermeer": "zoetermeer",
    "zwolle": "zwolle",
    "deventer": "deventer",
    "delft": "delft",
    "alkmaar": "alkmaar",
}

# Property types
PROPERTY_TYPES = {
    "all": "",
    "apartment": "appartement",
    "house": "woonhuis",
}

# CSS Selectors for listing page
LIST_SELECTORS = {
    "property_card": "article",
    "property_link": "a[href*='/']",
    "address": "h2",
    "location": "div",
    "price": "div",
    "features": "div",
    "agent": "div",
    "pagination_info": "nav div",
}

# CSS Selectors for detail page
DETAIL_SELECTORS = {
    "title": "div",
    "address": "div",
    "price": "div",
    "features_section": "div",
    "feature_list": "ul li",
    "description": "div",
    "agent_name": "a",
}
