"""
Orchestrates one full search: builds the query, fetches results, filters,
de-dupes, and optionally enriches with full Place Details.
"""
from typing import Optional

from places_client import search_places, get_place_details
from filters import apply_filters, deduplicate


def run_search(
    keyword: str,
    location_text: str,
    min_rating: Optional[float] = None,
    enrich_details: bool = False,
) -> list[dict]:
    """
    Run one keyword + location search end-to-end.

    keyword: business type to search for, e.g. "cafe", "salon"
    location_text: place name, e.g. "Sector 62, Noida" — passed straight to
                   Foursquare's `near` param, no separate geocoding needed.
    min_rating: optional minimum rating filter, 0-10 scale (Foursquare's scale,
                not Google's 0-5 — e.g. use 7.0 for a "4+ star" equivalent)
    enrich_details: if True, fetches full details per passing result again
                     (rarely needed here since search already returns rich
                     fields, but useful if you narrowed `fields` elsewhere)

    Returns a list of place dicts, filtered and de-duplicated.
    """
    raw_results = search_places(query=keyword, near=location_text)
    deduped = deduplicate(raw_results)
    filtered = apply_filters(deduped, keyword=keyword, min_rating=min_rating)

    if enrich_details:
        for place in filtered:
            details = get_place_details(place["fsq_id"])
            place.update(details)

    return filtered
