"""Main scraper class for Huispedia."""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from urllib.parse import urlencode, quote

import requests

from config import (
    SCRAPINGANT_API_KEY,
    SCRAPINGANT_API_URL,
    BASE_URL,
    SEARCH_URL,
    LOCATIONS,
    PROPERTY_TYPES,
    DEFAULT_MAX_WORKERS,
    DEFAULT_TIMEOUT,
)
from models import Property
from utils import parse_property_cards, parse_detail_page, get_pagination_info

logger = logging.getLogger(__name__)


class HuispediaScraper:
    """Scraper for Huispedia.nl property listings."""

    def __init__(self, api_key: Optional[str] = None, max_workers: int = DEFAULT_MAX_WORKERS):
        """Initialize the scraper.

        Args:
            api_key: ScrapingAnt API key (defaults to environment variable)
            max_workers: Maximum number of parallel requests
        """
        self.api_key = api_key or SCRAPINGANT_API_KEY
        if not self.api_key:
            raise ValueError(
                "ScrapingAnt API key is required. "
                "Set SCRAPINGANT_API_KEY environment variable or pass api_key parameter."
            )
        self.max_workers = max_workers
        self.session = requests.Session()

    def _fetch_page(self, url: str, wait_for: str = None) -> Optional[str]:
        """Fetch a page using ScrapingAnt API.

        Args:
            url: URL to fetch
            wait_for: CSS selector to wait for (optional)

        Returns:
            HTML content of the page
        """
        params = {
            "url": url,
            "x-api-key": self.api_key,
            "browser": "true",
        }

        try:
            logger.debug(f"Fetching: {url}")
            response = self.session.get(
                SCRAPINGANT_API_URL,
                params=params,
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def _build_list_url(self, location: str, page: int = 1, property_type: str = "") -> str:
        """Build URL for listing page.

        Args:
            location: City name
            page: Page number
            property_type: Property type filter

        Returns:
            URL for the listing page
        """
        # Base search URL
        url = f"{SEARCH_URL}/{location}"

        # Add property type filter if specified
        if property_type:
            url += f"/{property_type}"

        # Add pagination using query state
        if page > 1:
            skip = (page - 1) * 10
            search_state = {
                "pagination": {"currentPage": page, "skip": skip, "take": 10},
                "filter": {"sort": "homes_for_you"}
            }
            # For pages > 1, use the pagination path format
            url += f"/{page}_p"

        return url

    def _get_property_urls_from_page(self, html: str) -> List[dict]:
        """Extract property URLs and basic info from listing page.

        Args:
            html: HTML content of listing page

        Returns:
            List of property data dictionaries
        """
        return parse_property_cards(html)

    def _fetch_property_details(self, prop_data: dict) -> Optional[Property]:
        """Fetch and parse property detail page.

        Args:
            prop_data: Dictionary with basic property info

        Returns:
            Property object with full details
        """
        url = prop_data.get('url')
        if not url:
            return None

        html = self._fetch_page(url, wait_for="main")
        if not html:
            return None

        # Create Property object with basic info
        prop = Property(
            url=url,
            listing_id=prop_data.get('listing_id', ''),
            street_address=prop_data.get('street_address', ''),
            price=prop_data.get('price'),
            price_type=prop_data.get('price_type', ''),
            living_area=prop_data.get('living_area'),
            plot_size=prop_data.get('plot_size'),
            rooms=prop_data.get('rooms'),
            value_comparison=prop_data.get('value_comparison', ''),
            agent_name=prop_data.get('agent_name', ''),
        )

        # Parse location from basic data
        location = prop_data.get('location', '')
        if location:
            parts = location.split()
            if len(parts) >= 3:
                prop.postal_code = ' '.join(parts[:2])
                prop.city = ' '.join(parts[2:])

        # Enrich with detail page data
        return parse_detail_page(html, prop)

    def scrape(
        self,
        location: str = "amsterdam",
        property_type: str = "all",
        max_pages: Optional[int] = None,
        limit: Optional[int] = None,
        fetch_details: bool = True,
    ) -> List[Property]:
        """Scrape property listings from Huispedia.

        Args:
            location: City to search (default: amsterdam)
            property_type: Type of property (all, apartment, house)
            max_pages: Maximum number of pages to scrape
            limit: Maximum number of properties to return
            fetch_details: Whether to fetch detail pages

        Returns:
            List of Property objects
        """
        # Normalize location
        location_key = location.lower().replace(" ", "-")
        if location_key not in LOCATIONS:
            logger.warning(f"Location '{location}' not in predefined list, using as-is")
        location_slug = LOCATIONS.get(location_key, location_key)

        # Get property type filter
        prop_filter = PROPERTY_TYPES.get(property_type, "")

        logger.info(f"Starting scrape for {location} ({property_type})")

        all_properties = []
        page = 1

        while True:
            # Check limits
            if max_pages and page > max_pages:
                logger.info(f"Reached max pages limit: {max_pages}")
                break

            if limit and len(all_properties) >= limit:
                logger.info(f"Reached property limit: {limit}")
                break

            # Build URL and fetch page
            url = self._build_list_url(location_slug, page, prop_filter)
            logger.info(f"Fetching page {page}: {url}")

            html = self._fetch_page(url, wait_for="article")
            if not html:
                logger.warning(f"Failed to fetch page {page}")
                break

            # Parse properties from page
            properties = self._get_property_urls_from_page(html)
            if not properties:
                logger.info(f"No properties found on page {page}, stopping")
                break

            logger.info(f"Found {len(properties)} properties on page {page}")
            all_properties.extend(properties)

            # Get pagination info
            start, end, total = get_pagination_info(html)
            if total > 0:
                logger.info(f"Pagination: {start}-{end} of {total}")

            # Check if there are more pages
            if end >= total or len(properties) < 10:
                logger.info("Reached last page")
                break

            page += 1
            time.sleep(0.5)  # Rate limiting

        # Apply limit
        if limit:
            all_properties = all_properties[:limit]

        logger.info(f"Total properties found: {len(all_properties)}")

        # Fetch detail pages if requested
        if fetch_details and all_properties:
            logger.info("Fetching detail pages...")
            detailed_properties = []

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_prop = {
                    executor.submit(self._fetch_property_details, prop): prop
                    for prop in all_properties
                }

                for future in as_completed(future_to_prop):
                    prop_data = future_to_prop[future]
                    try:
                        prop = future.result()
                        if prop:
                            detailed_properties.append(prop)
                            logger.debug(f"Fetched details for {prop.street_address}")
                    except Exception as e:
                        logger.error(f"Error fetching details: {e}")

            return detailed_properties

        # Return basic Property objects without details
        return [
            Property(
                url=p.get('url', ''),
                listing_id=p.get('listing_id', ''),
                street_address=p.get('street_address', ''),
                price=p.get('price'),
                price_type=p.get('price_type', ''),
                living_area=p.get('living_area'),
                plot_size=p.get('plot_size'),
                rooms=p.get('rooms'),
                value_comparison=p.get('value_comparison', ''),
                agent_name=p.get('agent_name', ''),
            )
            for p in all_properties
        ]
