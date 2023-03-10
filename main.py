from olx_scraper import OlxScraper
from listings import Listings


def main():
    scraper = OlxScraper()
    listings = Listings()
    scraper.start_requests_session()
    scraper.start_discord_bot_session()
    scraper.get_all_pages()
    for p in range(scraper.page_number):
        listings.add_unv_listings(scraper.get_listings_from_page(p))
        listings.validate_listings()

    listings.sort_listings_by_price()
    listings.sort_listings_by_key_priority()
    # listings.save_listings_to_csv()
    # listings.open_new_listings_csv()

    for listing in listings.val_offers:
        if not listing.sent2discord:
            scraper.discord_bot.send_new_listing(listing)


if __name__ == "__main__":
    main()
