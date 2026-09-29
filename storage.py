"""
Flattens raw Foursquare place dicts into rows and writes them out.
"""
import os
from datetime import datetime
from typing import Optional

import pandas as pd

from config import OUTPUT_DIR


def build_address(location: dict) -> str:
    """
    Assemble a readable address from location parts. The current API doesn't
    always provide a single pre-formatted address string, so build one from
    whichever parts are present.
    """
    parts = [
        location.get("address"),
        location.get("locality"),
        location.get("region"),
        location.get("postcode"),
        location.get("country"),
    ]
    return ", ".join(p for p in parts if p)


def flatten_place(place: dict) -> dict:
    """Pull out the fields we actually care about into a flat row."""
    location = place.get("location", {})
    categories = ", ".join(c.get("name", "") for c in place.get("categories", []))

    return {
        "fsq_place_id": place.get("fsq_place_id"),
        "name": place.get("name"),
        "address": build_address(location),
        "rating": place.get("rating"),  # 0-10 scale, may require a paid plan
        "price": place.get("price"),  # 1-4 scale, may require a paid plan
        "categories": categories,
        "lat": place.get("latitude"),
        "lng": place.get("longitude"),
        "date_closed": place.get("date_closed"),
        "phone": place.get("tel"),
        "website": place.get("website"),
    }


def save_to_csv(places: list[dict], filename: Optional[str] = None) -> str:
    """Flatten a list of place dicts and write them to a timestamped CSV."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_{timestamp}.csv"
    filepath = os.path.join(OUTPUT_DIR, filename)

    rows = [flatten_place(p) for p in places]
    df = pd.DataFrame(rows)
    df.to_csv(filepath, index=False)
    return filepath
