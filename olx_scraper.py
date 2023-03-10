from settings import SETTINGS
from bs4 import BeautifulSoup
from bot import MyBot
import requests
import re


class OlxScraper:
    def __init__(self) -> None:
        self.base_url = SETTINGS["base_url"]
        self.product = f"oferty/q-{'-'.join(SETTINGS['product_name'].split())}/"
        self.filters = {
            "search[filter_float_price:from]": SETTINGS["limits"]["lower_limit"],
            "search[filter_float_price:to]": SETTINGS["limits"]["upper_limit"],
        }
        self.limits = SETTINGS["limits"]

    def start_requests_session(self):  # starts new requests session
        self.session = requests.Session()

    def start_discord_bot_session(self):  # starts new discord bot session:
        with open("TOKEN.txt", "r") as f:
            TOKEN = f.read()
        self.discord_bot = MyBot(command_prefix="-", self_bot=False)
        self.discord_bot.run(TOKEN)

    def url(self):  # returns url w/o filter
        return self.base_url + self.product

    def get_all_pages(self):  # sets ammout of pages considering filters
        try:
            response = self.session.get(self.url(), params=self.filters, timeout=10)
        except TimeoutError:
            print("Request timeout, check your connection")

        soup = BeautifulSoup(response.content, "lxml")
        self.page_number = int(
            soup.find_all("li", {"data-testid": "pagination-list-item"})[-1].text
        )

    def get_listings_from_page(
        self, page
    ):  # fetches all available listings from a given page
        self.filters["page"] = page + 1
        response = self.session.get(self.url(), params=self.filters)
        soup = BeautifulSoup(response.content, "lxml")
        return soup.find(
            "div", class_=re.compile(r"listing-grid-container.*")
        ).find_all("div", {"data-cy": "l-card"})
