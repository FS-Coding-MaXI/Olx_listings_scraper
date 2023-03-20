from settings import OLX_SETTINGS
from bs4 import BeautifulSoup
import requests
import re


class OlxScraper:
    def __init__(self) -> None:
        self.base_url = OLX_SETTINGS["base_url"]
        self.product = f"oferty/q-{'-'.join(OLX_SETTINGS['product_name'].split())}/"
        self.filters = {
            "search[filter_float_price:from]": OLX_SETTINGS["limits"]["lower_limit"],
            "search[filter_float_price:to]": OLX_SETTINGS["limits"]["upper_limit"],
        }
        self.limits = OLX_SETTINGS["limits"]

    # starts new requests session
    def start_requests_session(self):
        self.session = requests.Session()

    # returns url w/o filter
    def url(self):
        return self.base_url + self.product

    # sets ammout of pages considering filters
    def get_all_pages(self):
        response = self.session.get(self.url(), params=self.filters)

        soup = BeautifulSoup(response.content, "html.parser")
        try:
            self.page_number = int(
                soup.find_all("li", {"data-testid": "pagination-list-item"})[-1].text
            )
        except (AttributeError, IndexError):
            self.get_all_pages()

    # fetches all available listings from a given page
    def get_listings_from_page(self, page):
        self.filters["page"] = page + 1
        response = self.session.get(self.url(), params=self.filters)
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            return soup.find(
                "div", class_=re.compile(r"listing-grid-container.*")
            ).find_all("div", {"data-cy": "l-card"})
        except AttributeError:
            self.get_listings_from_page(page)

    def get_single_listing_photo(self, ls_url):
        response = self.session.get(url=ls_url)
        soup = BeautifulSoup(response.content, "html.parser")
        try:
            image_link = (
                soup.find("div", {"class": "swiper-zoom-container"})
                .find("img")
                .attrs["src"]
            )
            return image_link
        except:
            return "https://cdn.pixabay.com/photo/2019/03/13/14/07/question-4052948__340.png"
