"""
CLI entry point. Example:

    python main.py --keyword cafe --location "Sector 62, Noida" --min-rating 7.0
"""
import argparse

from scraper import run_search
from storage import save_to_csv


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape business leads from Foursquare Places API.")
    parser.add_argument("--keyword", required=True, help='Business type, e.g. "cafe", "salon"')
    parser.add_argument("--location", required=True, help='Location bracket, e.g. "Sector 62, Noida"')
    parser.add_argument("--min-rating", type=float, default=None, help="Optional minimum rating filter, 0-10 scale")
    parser.add_argument("--enrich", action="store_true", help="Re-fetch full details per result (usually unnecessary)")
    return parser.parse_args()


def main():
    args = parse_args()

    print(f"Searching for '{args.keyword}' in '{args.location}'...")
    results = run_search(
        keyword=args.keyword,
        location_text=args.location,
        min_rating=args.min_rating,
        enrich_details=args.enrich,
    )

    print(f"Found {len(results)} matching businesses after filtering.")
    filepath = save_to_csv(results)
    print(f"Saved to {filepath}")


if __name__ == "__main__":
    main()
