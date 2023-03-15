from bot import MyBot
from listings import Listings
from olx_scraper import OlxScraper


def single_scrap():
    listings = Listings()
    scraper = OlxScraper()
    scraper.start_requests_session()
    scraper.get_all_pages()
    for p in range(scraper.page_number):
        listings.add_unv_listings(scraper.get_listings_from_page(p))
        listings.validate_listings()

    listings.sort_listings_by_price()
    listings.sort_listings_by_key_priority()
    listings.listings_to_csv()
    listings.open_new_listings_csv()


def discord_interactive_bot():
    with open("TOKEN.txt", "r") as f:
        TOKEN = f.read()
    discord_bot = MyBot(command_prefix="-", self_bot=False)
    discord_bot.run(TOKEN)


def choose_mode():

    print("1. Scrap listings for a single time and open the results.")
    print("2. Run a discord interactive scraper.")
    try:
        choose = int(input("Choose one of the possible modes: ")[0])
        if choose == 1:
            single_scrap()
        elif choose == 2:
            discord_interactive_bot()
    except:
        choose_mode()


if __name__ == "__main__":
    choose_mode()
