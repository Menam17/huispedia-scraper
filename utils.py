"""Utility functions for parsing Huispedia pages."""

import re
import logging
from typing import Optional, List, Tuple
from bs4 import BeautifulSoup, Tag

from models import Property
from config import BASE_URL

logger = logging.getLogger(__name__)


def parse_price(text: str) -> Tuple[Optional[int], str]:
    """Extract price value and type from text.

    Args:
        text: Price text like "€ 310.000 k.k." or "€ 425.000 v.o.n."

    Returns:
        Tuple of (price_value, price_type)
    """
    if not text:
        return None, ""

    # Extract price type
    price_type = ""
    if "k.k." in text.lower():
        price_type = "k.k."
    elif "v.o.n." in text.lower():
        price_type = "v.o.n."

    # Extract numeric value
    match = re.search(r'€\s*([\d.]+)', text.replace(',', '.'))
    if match:
        try:
            # Remove dots used as thousand separators
            price_str = match.group(1).replace('.', '')
            return int(price_str), price_type
        except ValueError:
            pass

    return None, price_type


def parse_area(text: str) -> Optional[int]:
    """Extract area in m² from text.

    Args:
        text: Area text like "112 m²" or "145 m² perceel"

    Returns:
        Area value in m²
    """
    if not text:
        return None

    match = re.search(r'(\d+)\s*m[²2]', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    return None


def parse_rooms(text: str) -> Optional[int]:
    """Extract number of rooms from text.

    Args:
        text: Text like "4 kamers" or "4 kamers (3 slaapkamers)"

    Returns:
        Number of rooms
    """
    if not text:
        return None

    match = re.search(r'(\d+)\s*kamer', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    return None


def parse_bedrooms(text: str) -> Optional[int]:
    """Extract number of bedrooms from text.

    Args:
        text: Text like "4 kamers (3 slaapkamers)"

    Returns:
        Number of bedrooms
    """
    if not text:
        return None

    match = re.search(r'(\d+)\s*slaapkamer', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    return None


def parse_year(text: str) -> Optional[int]:
    """Extract year from text.

    Args:
        text: Text containing a year like "1950" or "Bouwjaar: 1950"

    Returns:
        Year value
    """
    if not text:
        return None

    match = re.search(r'\b(19\d{2}|20\d{2})\b', text)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    return None


def extract_listing_id(url: str) -> str:
    """Extract listing ID from URL.

    Args:
        url: Property URL like "/amsterdam/1012ab/damstraat/1"

    Returns:
        Listing ID (the URL path as identifier)
    """
    if not url:
        return ""

    # Remove base URL if present
    url = url.replace(BASE_URL, "")

    # Clean up the path
    parts = [p for p in url.strip("/").split("/") if p]
    if len(parts) >= 4:
        return "-".join(parts[:4])

    return url.strip("/").replace("/", "-")


def parse_property_cards(html: str) -> List[dict]:
    """Parse property cards from listing page.

    Args:
        html: HTML content of the listing page

    Returns:
        List of dictionaries with basic property info
    """
    soup = BeautifulSoup(html, 'lxml')
    properties = []

    # Find all article elements (property cards)
    articles = soup.find_all('article')

    for article in articles:
        try:
            # Skip ad articles
            if article.find(string=re.compile(r'Advertentie', re.I)):
                continue

            # Find property link
            link = article.find('a', href=re.compile(r'^/[a-z\-]+/\d+[a-z]+/'))
            if not link:
                continue

            href = link.get('href', '')
            if not href or href.startswith('http'):
                continue

            url = f"{BASE_URL}{href}"

            # Extract address from h2
            h2 = article.find('h2')
            address = h2.get_text(strip=True) if h2 else ""

            # Extract location (postal code + city)
            location = ""
            location_div = article.find(string=re.compile(r'\d{4}\s*[A-Z]{2}'))
            if location_div:
                location = location_div.strip()

            # Extract price
            price = None
            price_type = ""
            price_text = article.find(string=re.compile(r'€\s*[\d.]+'))
            if price_text:
                price, price_type = parse_price(price_text.strip())

            # Extract area
            living_area = None
            plot_size = None
            area_matches = article.find_all(string=re.compile(r'\d+\s*m[²2]'))
            for i, area_text in enumerate(area_matches):
                area_val = parse_area(area_text)
                if area_val:
                    if i == 0:
                        living_area = area_val
                    elif 'perceel' in area_text.lower() or i == 1:
                        plot_size = area_val

            # Extract rooms
            rooms = None
            rooms_text = article.find(string=re.compile(r'\d+\s*kamer'))
            if rooms_text:
                rooms = parse_rooms(rooms_text)

            # Extract value comparison
            value_comparison = ""
            for val in ["Onder de waarde", "Binnen de waarde", "Boven de waarde"]:
                if article.find(string=re.compile(val, re.I)):
                    value_comparison = val
                    break

            # Extract agent name (usually last div in the card)
            agent_name = ""
            divs = article.find_all('div')
            for div in reversed(divs):
                text = div.get_text(strip=True)
                if text and len(text) > 3 and not text.startswith('€') and 'm²' not in text:
                    if not any(skip in text.lower() for skip in ['kamer', 'waarde', 'prijs', 'nieuw']):
                        agent_name = text
                        break

            prop_data = {
                'url': url,
                'listing_id': extract_listing_id(href),
                'street_address': address,
                'location': location,
                'price': price,
                'price_type': price_type,
                'living_area': living_area,
                'plot_size': plot_size,
                'rooms': rooms,
                'value_comparison': value_comparison,
                'agent_name': agent_name,
            }

            properties.append(prop_data)

        except Exception as e:
            logger.debug(f"Error parsing property card: {e}")
            continue

    return properties


def parse_detail_page(html: str, prop: Property) -> Property:
    """Parse property detail page and enrich Property object.

    Args:
        html: HTML content of the detail page
        prop: Property object to enrich

    Returns:
        Enriched Property object
    """
    soup = BeautifulSoup(html, 'lxml')

    try:
        # Extract title from page
        title_elem = soup.find('title')
        if title_elem:
            prop.title = title_elem.get_text(strip=True)

        # Find all list items with property features
        all_items = soup.find_all('li')

        for item in all_items:
            text = item.get_text(" ", strip=True)

            # Price details
            if 'Vraagprijs' in text and '€' in text:
                price, price_type = parse_price(text)
                if price:
                    prop.price = price
                    prop.price_type = price_type

            if 'Vraagprijs per m' in text:
                match = re.search(r'€\s*([\d.]+)', text)
                if match:
                    try:
                        prop.price_per_sqm = int(match.group(1).replace('.', ''))
                    except ValueError:
                        pass

            # Status
            if 'Aangeboden sinds' in text:
                prop.listed_since = text.replace('Aangeboden sinds', '').strip()

            if 'Status' in text:
                prop.status = text.replace('Status', '').strip()

            if 'Aanvaarding' in text:
                prop.acceptance = text.replace('Aanvaarding', '').strip()

            # Building info
            if 'Soort woonhuis' in text:
                parts = text.replace('Soort woonhuis', '').strip().split(',')
                if parts:
                    prop.property_type = parts[0].strip()
                    if len(parts) > 1:
                        prop.house_type = parts[1].strip()

            if 'Soort bouw' in text:
                prop.build_type = text.replace('Soort bouw', '').strip()

            if 'Bouwjaar' in text and 'Cv-ketel' not in text:
                prop.year_built = parse_year(text)

            if 'Renovatiejaar' in text:
                prop.renovation_year = parse_year(text)

            if 'Soort dak' in text:
                prop.roof_type = text.replace('Soort dak', '').strip()

            # Energy
            if 'Energielabel' in text:
                match = re.search(r'\b([A-G](\+{1,3})?)\b', text)
                if match:
                    prop.energy_label = match.group(1)

            if 'Isolatie' in text:
                prop.insulation = text.replace('Isolatie', '').strip()

            if 'Verwarming' in text:
                prop.heating = text.replace('Verwarming', '').strip()

            if 'Cv-ketel bouwjaar' in text:
                prop.cv_year = parse_year(text)

            # Dimensions
            if 'Woonoppervlakte' in text:
                prop.living_area = parse_area(text)

            if 'Perceeloppervlakte' in text:
                prop.plot_size = parse_area(text)

            if 'Inhoud' in text:
                match = re.search(r'(\d+)\s*m[³3]', text)
                if match:
                    try:
                        prop.volume = int(match.group(1))
                    except ValueError:
                        pass

            # Rooms
            if 'Aantal kamers' in text:
                prop.rooms = parse_rooms(text)
                prop.bedrooms = parse_bedrooms(text)

            if 'Aantal badkamers' in text:
                match = re.search(r'(\d+)\s*badkamer', text)
                if match:
                    try:
                        prop.bathrooms = int(match.group(1))
                    except ValueError:
                        pass

            if 'Aantal woonlagen' in text:
                match = re.search(r'(\d+)\s*woonla', text)
                if match:
                    try:
                        prop.floors = int(match.group(1))
                    except ValueError:
                        pass

            # Kitchen
            if 'Keuken' in text and 'voorzieningen' not in text.lower():
                prop.kitchen_type = text.replace('Keuken', '').strip()

            if 'Keukenvoorzieningen' in text:
                prop.kitchen_amenities = text.replace('Keukenvoorzieningen', '').strip()

            # Bathroom
            if 'Badkamervoorzieningen' in text:
                prop.bathroom_amenities = text.replace('Badkamervoorzieningen', '').strip()

            # Location
            if 'Ligging woning' in text:
                prop.location_type = text.replace('Ligging woning', '').strip()

            # Parking
            if 'Soort parkeergelegenheid' in text:
                prop.parking_type = text.replace('Soort parkeergelegenheid', '').strip()

            # Maintenance
            if text.startswith('Binnen') and 'Buiten' not in text:
                prop.maintenance_inside = text.replace('Binnen', '').strip()

            if text.startswith('Buiten'):
                prop.maintenance_outside = text.replace('Buiten', '').strip()

            # Cadastral
            if 'Oppervlakte' not in text and re.match(r'^[A-Z]+ [A-Z] \d+', text):
                prop.cadastral_info = text

        # Extract description
        # Look for long text blocks that appear to be descriptions
        for div in soup.find_all('div'):
            text = div.get_text(" ", strip=True)
            if len(text) > 500 and not div.find('ul') and not div.find('nav'):
                # Check if this looks like a description
                if any(word in text.lower() for word in ['woning', 'kamer', 'keuken', 'tuin', 'badkamer']):
                    prop.description = text[:2000]  # Limit length
                    break

        # Extract agent info
        agent_link = soup.find('a', href=re.compile(r'/makelaars/kantoor/'))
        if agent_link:
            prop.agent_name = agent_link.get_text(strip=True)
            prop.agent_url = BASE_URL + agent_link.get('href', '')

        # Extract city and postal code from breadcrumbs or address
        breadcrumb = soup.find('nav', {'aria-label': True})
        if breadcrumb:
            links = breadcrumb.find_all('a')
            for link in links:
                href = link.get('href', '')
                if '/koopwoningen/' in href:
                    city = href.replace('/koopwoningen/', '').strip('/')
                    if city and city != 'provincie-':
                        prop.city = city.replace('-', ' ').title()

        # Try to extract postal code from page
        postal_match = soup.find(string=re.compile(r'\d{4}\s*[A-Z]{2}'))
        if postal_match:
            match = re.search(r'(\d{4}\s*[A-Z]{2})', postal_match)
            if match:
                prop.postal_code = match.group(1).replace(' ', ' ')

    except Exception as e:
        logger.error(f"Error parsing detail page: {e}")

    return prop


def get_total_count(html: str) -> int:
    """Extract total property count from listing page.

    Args:
        html: HTML content of the listing page

    Returns:
        Total number of properties
    """
    soup = BeautifulSoup(html, 'lxml')

    # Look for heading with count
    h1 = soup.find('h1')
    if h1:
        text = h1.get_text()
        match = re.search(r'([\d.]+)\s*Koopwoningen', text)
        if match:
            try:
                return int(match.group(1).replace('.', ''))
            except ValueError:
                pass

    # Look for pagination info
    nav = soup.find('nav')
    if nav:
        text = nav.get_text()
        match = re.search(r'van\s*([\d.]+)', text)
        if match:
            try:
                return int(match.group(1).replace('.', ''))
            except ValueError:
                pass

    return 0


def get_pagination_info(html: str) -> Tuple[int, int, int]:
    """Extract pagination info from listing page.

    Args:
        html: HTML content of the listing page

    Returns:
        Tuple of (current_start, current_end, total_count)
    """
    soup = BeautifulSoup(html, 'lxml')

    # Look for text like "Resultaten 1-10 van 58.480"
    for nav in soup.find_all('nav'):
        text = nav.get_text()
        match = re.search(r'Resultaten?\s*(\d+)-(\d+)\s*van\s*([\d.]+)', text)
        if match:
            try:
                start = int(match.group(1))
                end = int(match.group(2))
                total = int(match.group(3).replace('.', ''))
                return start, end, total
            except ValueError:
                pass

    return 0, 0, 0
