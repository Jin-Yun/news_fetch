#!/usr/bin/env python3
"""
Example usage of the SpanishNewsCrawler.

This demonstrates both:
1. Running as a script that outputs a JSON file
2. Importing as a module and getting results in-code
"""

from news_fetch import SpanishNewsCrawler


def example_module_import():
    """
    Example: Import as module and get results programmatically
    """
    print("=== Example: Module import usage ===")
    print("Searching for 'China' in El País and EFE from 2025-01-01 to 2025-03-28")
    print()

    crawler = SpanishNewsCrawler(
        keywords="China",
        start_date="2025-01-01",
        end_date="2025-03-28",
        media_sites=["elpais", "efe"],
        delay_seconds=3.0,
    )

    # Run and get result dictionary
    result = crawler.run()

    print(f"Total articles found: {result['crawl_info']['total_news']}")
    print(f"Status: {result['crawl_info']['status']}")
    print(f"Crawl time: {result['crawl_info']['crawl_time_seconds']}s")
    print()

    # Access article list
    articles = result['news_data']
    if articles:
        print("First article:")
        print(f"  Title: {articles[0]['title']}")
        print(f"  Source: {articles[0]['media']}")
        print(f"  Published: {articles[0]['publish_time']}")
        print(f"  URL: {articles[0]['url']}")

    return result


def example_save_to_file():
    """
    Example: Run crawler and save results to JSON file
    """
    print("\n=== Example: Save to JSON file ===")

    crawler = SpanishNewsCrawler(
        keywords=["China", "Asia"],
        start_date="2025-01-01",
        end_date="2025-03-28",
        media_sites=None,  # None means all sites
        delay_seconds=3.0,
    )

    # This automatically runs and saves
    output_file = "spanish_news_china_asia.json"
    crawler.save_to_json(output_file)

    print(f"Results saved to: {output_file}")


def example_multiple_keywords_all_sites():
    """
    Example: Multiple keywords across all supported sites
    """
    print("\n=== Example: Multiple keywords on all sites ===")

    crawler = SpanishNewsCrawler(
        keywords=["China", "Asia", "Pekín", "Beijing"],  # Can search with Spanish terms too
        start_date="2024-01-01",
        end_date="2024-12-31",
        # media_sites omitted = all sites
    )

    result = crawler.run()

    print(f"Found {result['crawl_info']['total_news']} total articles across {len(crawler.media_sites)} sites")


if __name__ == "__main__":
    # Run first example - module import usage
    example_module_import()

    # Uncomment below to run full examples
    # example_save_to_file()
    # example_multiple_keywords_all_sites()
