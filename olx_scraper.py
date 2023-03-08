from settings import SETTINGS
from bs4 import BeautifulSoup
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

    def start_session(self):  # starts new requests session
        self.session = requests.Session()

    def url(self):  # returns url w/o filter
        return self.base_url + self.product

    def get_all_pages(self):  # sets ammout of pages considering filters
        response = self.session.get(self.url(), params=self.filters)
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