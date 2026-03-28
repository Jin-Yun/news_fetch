#!/usr/bin/env python3
"""
Command-line interface for SpanishNewsCrawler.

Example usage:
    python cli.py --keywords "China Asia" --start 2025-01-01 --end 2025-03-28 --media elpais efe --output results.json
"""

import argparse
import sys
from news_fetch import SpanishNewsCrawler


def main():
    parser = argparse.ArgumentParser(
        description="Crawl Spanish news about China/Asia from major Spanish media outlets."
    )

    parser.add_argument(
        "--keywords", "-k",
        required=True,
        help="Search keywords (space-separated, quote if multiple)",
    )
    parser.add_argument(
        "--start", "-s",
        required=True,
        help="Start date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--end", "-e",
        required=True,
        help="End date in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--media", "-m",
        nargs="+",
        help="List of media sites to crawl (default: all available)",
        choices=["elpais", "elmundo", "abc", "efe"],
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Output JSON file path",
    )
    parser.add_argument(
        "--delay", "-d",
        type=float,
        default=3.0,
        help="Delay between requests in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--no-deduplicate",
        action="store_true",
        help="Disable duplicate URL deduplication",
    )

    args = parser.parse_args()

    # Create crawler
    crawler = SpanishNewsCrawler(
        keywords=args.keywords,
        start_date=args.start,
        end_date=args.end,
        media_sites=args.media,
        delay_seconds=args.delay,
        deduplicate=not args.no_deduplicate,
    )

    print(f"Starting crawl with parameters:")
    print(f"  Keywords: {crawler.keywords}")
    print(f"  Date range: {args.start} to {args.end}")
    print(f"  Media sites: {crawler.media_sites}")
    print(f"  Output to: {args.output}")
    print()

    # Run and save
    result = crawler.run()

    print(f"\nCrawl complete:")
    print(f"  Status: {result['crawl_info']['status']}")
    print(f"  Total articles: {result['crawl_info']['total_news']}")
    print(f"  Time elapsed: {result['crawl_info']['crawl_time_seconds']}s")

    crawler.save_to_json(args.output)
    print(f"\nResults saved to: {args.output}")

    if result['crawl_info']['status'] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
