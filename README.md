# Business lead scraper (Foursquare Places API)

Fetches businesses by keyword + location using the Foursquare Places API,
filters and de-dupes them, and saves the results to CSV.

## Setup

1. Create a free Foursquare developer account at developer.foursquare.com,
   create a project, and generate a **Service API Key** from the Developer
   Console (Manage Service API Keys). Free tier includes starter credit.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and paste in your key:
   ```
   cp .env.example .env
   ```

## Usage

```
python main.py --keyword cafe --location "Sector 62, Noida" --min-rating 7.0
```

Note: Foursquare rates on a **0-10 scale**, not Google's 0-5 stars — 7.0 is
roughly a solid rating, 8.5+ is excellent.

Optional flags:
- `--min-rating 7.0` — only keep businesses at/above this rating (0-10 scale)
- `--enrich` — re-fetch full place details per result (rarely needed, since
  search already returns rich fields including phone/website)

Output is saved as a timestamped CSV in `output/`.

## Project structure

```
gmaps_scraper/
├── config.py          # loads API key, holds tunable constants
├── places_client.py   # Foursquare API wrapper: search_places, get_place_details
├── filters.py         # keyword/rating/closed-status filtering + de-duplication
├── storage.py         # flattens results and writes CSV
├── scraper.py         # orchestrates one full search end-to-end
├── main.py            # CLI entry point
├── requirements.txt
└── .env.example
```

## What changed from the Google Maps version

- No separate geocoding step — Foursquare's `near` parameter accepts a place
  name directly ("Sector 62, Noida") and resolves it server-side.
- Pagination works differently: Foursquare returns a `next` URL in the
  response's `Link` header rather than a `next_page_token` string. This is
  handled inside `search_places()` in `places_client.py`.
- Field names differ: `fsq_id` instead of `place_id`, `location.formatted_address`
  instead of `formatted_address`, ratings are 0-10 instead of 0-5.
- `closed_bucket` replaces Google's `business_status` for filtering out
  likely-closed businesses — it's a confidence label, not a hard fact, so
  the filter only drops "LikelyClosed"/"VeryLikelyClosed", not "Unsure".
- Some fields (rating, tel, website, stats) may be gated behind Foursquare's
  paid plan tiers — if they come back empty on your account, check your
  plan's field access in the Foursquare dashboard.

## Extending to a location grid (whole-city coverage)

`run_search()` currently does one search per call, capped at ~150 results
(3 pages x 50). For full-city coverage, loop `run_search()` over a grid of
sub-locations — e.g. a list of sector names or lat/lng points spaced ~2-3km
apart — and concatenate + de-duplicate the combined results before saving.
