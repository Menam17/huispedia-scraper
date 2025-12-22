"""Data models for Huispedia scraper."""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class Property:
    """Represents a property listing from Huispedia."""

    # Basic info
    url: str
    listing_id: str = ""
    title: str = ""

    # Address
    street_address: str = ""
    postal_code: str = ""
    city: str = ""
    province: str = ""

    # Price
    price: Optional[int] = None
    price_per_sqm: Optional[int] = None
    price_type: str = ""  # k.k. (kosten koper) or v.o.n. (vrij op naam)

    # Value comparison
    value_comparison: str = ""  # Onder/Binnen/Boven de waarde

    # Dimensions
    living_area: Optional[int] = None
    plot_size: Optional[int] = None
    volume: Optional[int] = None

    # Rooms
    rooms: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floors: Optional[int] = None

    # Property characteristics
    property_type: str = ""  # Eengezinswoning, Appartement, etc.
    house_type: str = ""  # Hoekwoning, Tussenwoning, etc.
    build_type: str = ""  # Bestaande bouw, Nieuwbouw
    year_built: Optional[int] = None
    renovation_year: Optional[int] = None

    # Energy
    energy_label: str = ""
    insulation: str = ""
    heating: str = ""
    cv_year: Optional[int] = None

    # Features
    roof_type: str = ""
    kitchen_type: str = ""
    kitchen_amenities: str = ""
    bathroom_amenities: str = ""

    # Location
    location_type: str = ""  # in het centrum, aan water, etc.
    parking_type: str = ""

    # Condition
    maintenance_inside: str = ""
    maintenance_outside: str = ""

    # Status
    status: str = ""
    listed_since: str = ""
    acceptance: str = ""

    # Cadastral
    cadastral_info: str = ""

    # Description
    description: str = ""

    # Agent
    agent_name: str = ""
    agent_url: str = ""

    # Metadata
    date_scraped: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert property to dictionary."""
        return {
            "url": self.url,
            "listing_id": self.listing_id,
            "title": self.title,
            "street_address": self.street_address,
            "postal_code": self.postal_code,
            "city": self.city,
            "province": self.province,
            "price": self.price,
            "price_per_sqm": self.price_per_sqm,
            "price_type": self.price_type,
            "value_comparison": self.value_comparison,
            "living_area": self.living_area,
            "plot_size": self.plot_size,
            "volume": self.volume,
            "rooms": self.rooms,
            "bedrooms": self.bedrooms,
            "bathrooms": self.bathrooms,
            "floors": self.floors,
            "property_type": self.property_type,
            "house_type": self.house_type,
            "build_type": self.build_type,
            "year_built": self.year_built,
            "renovation_year": self.renovation_year,
            "energy_label": self.energy_label,
            "insulation": self.insulation,
            "heating": self.heating,
            "cv_year": self.cv_year,
            "roof_type": self.roof_type,
            "kitchen_type": self.kitchen_type,
            "kitchen_amenities": self.kitchen_amenities,
            "bathroom_amenities": self.bathroom_amenities,
            "location_type": self.location_type,
            "parking_type": self.parking_type,
            "maintenance_inside": self.maintenance_inside,
            "maintenance_outside": self.maintenance_outside,
            "status": self.status,
            "listed_since": self.listed_since,
            "acceptance": self.acceptance,
            "cadastral_info": self.cadastral_info,
            "description": self.description,
            "agent_name": self.agent_name,
            "agent_url": self.agent_url,
            "date_scraped": self.date_scraped,
        }
