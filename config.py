"""
Central config: loads the API key from .env and holds tunable defaults.
"""
import os
from dotenv import load_dotenv

load_dotenv()

FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY")

if not FOURSQUARE_API_KEY:
    raise RuntimeError(
        "FOURSQUARE_API_KEY not set. Copy .env.example to .env and add your key."
    )

# Foursquare retired the old v3 API (api.foursquare.com/v3) in 2026.
# This is the current Places API.
FOURSQUARE_BASE_URL = "https://places-api.foursquare.com"
PLACES_API_VERSION = "2025-06-17"  # required header, only version currently allowed

# Foursquare's v3 search returns up to 50 results per page (max allowed by `limit`).
# Pagination beyond that follows the "link" URL in the response header.
RESULTS_PER_PAGE = 50
MAX_PAGES_PER_QUERY = 3  # mirrors the old cap of ~150 results per query

# Default search radius in meters when using ll+radius instead of a place name.
DEFAULT_RADIUS_METERS = 5000

# Output file defaults
OUTPUT_DIR = "output"
