"""
Thin wrapper around Foursquare's current Places API: search + pagination + place details.
Keeping this isolated means main.py and scraper.py don't touch the API directly.
"""
from typing import Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from config import (
    FOURSQUARE_API_KEY,
    FOURSQUARE_BASE_URL,
    PLACES_API_VERSION,
    RESULTS_PER_PAGE,
    MAX_PAGES_PER_QUERY,
)

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {FOURSQUARE_API_KEY}",
    "X-Places-Api-Version": PLACES_API_VERSION,
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def search_places(
    query: str,
    near: Optional[str] = None,
    ll: Optional[str] = None,
    radius: Optional[int] = None,
    fsq_category_ids: Optional[str] = None,
    limit: int = RESULTS_PER_PAGE,
) -> list[dict]:
    """
    Search Foursquare Places by keyword + location.

    query: business type keyword, e.g. "cafe"
    near: place name, e.g. "Sector 62, Noida" — Foursquare geocodes this for you.
    ll: alternative to `near` — "lat,lng" string, used with `radius` for precise control.
    radius: search radius in meters (only used alongside `ll`).
    fsq_category_ids: comma-separated Foursquare category IDs to filter by (optional).

    Follows pagination via the "link" URL in the response header, up to
    MAX_PAGES_PER_QUERY. Returns a list of raw place dicts as returned by the API.
    """
    params = {"query": query, "limit": limit}
    if near:
        params["near"] = near
    if ll:
        params["ll"] = ll
    if radius:
        params["radius"] = radius
    if fsq_category_ids:
        params["fsq_category_ids"] = fsq_category_ids

    all_results = []
    url = f"{FOURSQUARE_BASE_URL}/places/search"
    page_count = 0

    while url and page_count < MAX_PAGES_PER_QUERY:
        response = requests.get(url, headers=HEADERS, params=params if page_count == 0 else None)
        response.raise_for_status()
        data = response.json()
        all_results.extend(data.get("results", []))

        # Pagination is via a "link" URL in the response header, not a token.
        next_link = response.links.get("next", {}).get("url")
        url = next_link
        page_count += 1

    return all_results


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def get_place_details(fsq_place_id: str, fields: Optional[str] = None) -> dict:
    """
    Fetch full details for one place by its fsq_place_id — useful if you
    requested a narrower `fields` set during search and need more for passing results.
    """
    url = f"{FOURSQUARE_BASE_URL}/places/{fsq_place_id}"
    params = {"fields": fields} if fields else {}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json()
