"""
Post-fetch filtering: sharpen Foursquare's broad matches down to what the
user actually asked for, and drop anything that looks closed or low quality.
"""
from typing import Optional


def matches_keyword(place: dict, keyword: str) -> bool:
    """
    Secondary keyword check against name + category names, since Foursquare's
    `query` search can return loosely-related results.
    """
    keyword_lower = keyword.lower()
    name = place.get("name", "").lower()
    category_names = " ".join(c.get("name", "") for c in place.get("categories", [])).lower()
    return keyword_lower in name or keyword_lower in category_names


def meets_minimum_rating(place: dict, min_rating: Optional[float]) -> bool:
    """
    Optional quality filter. Foursquare ratings are on a 0-10 scale (not 0-5
    like Google). Note: rating may only be available on paid Foursquare plan
    tiers — if it's consistently missing, this filter will drop everything.
    """
    if min_rating is None:
        return True
    rating = place.get("rating")
    return rating is not None and rating >= min_rating


def is_operational(place: dict) -> bool:
    """
    Drop places Foursquare has recorded a closure date for. Places with no
    `date_closed` field are treated as open (most places won't have this field).
    """
    return not place.get("date_closed")


def apply_filters(places: list[dict], keyword: str, min_rating: Optional[float] = None) -> list[dict]:
    """Run the full filter chain and return only the places that pass all of them."""
    return [
        p for p in places
        if matches_keyword(p, keyword)
        and meets_minimum_rating(p, min_rating)
        and is_operational(p)
    ]


def deduplicate(places: list[dict]) -> list[dict]:
    """De-dupe by fsq_place_id (not name — chains share names across branches)."""
    seen_ids = set()
    unique = []
    for p in places:
        pid = p.get("fsq_place_id")
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            unique.append(p)
    return unique
