import requests
from bs4 import BeautifulSoup
import re
import locale
import csv
import time
import json
import os

SETTINGS = json.load(open("settings.json"))
LOG_NAME = (
    "olx_scraper_"
    + "-".join((time.strftime("%D_%H-%M-%S", time.localtime())).split("/"))
    + ".csv"
)


class Listing:
    def __init__(self, listing) -> None:
        self.listing_code = listing
        self.listing_name = listing.find("h6").text

    def __getitem__(self):  # makes Listing subscriptable by price
        return getattr(self, "price")

    def _is_highlighted(self):
        return (
            self.listing_code.find("div", {"data-testid": "adCard-featured"})
            is not None
        )  ## if not None, then it is highlighted

    def _create_full_data(self):  # fetches validated listing data
        try:
            self.condition = self.listing_code.find(
                "span", {"title": re.compile(r".*")}
            ).text
        except AttributeError:  # if there isn't such as span
            self.condition = "Unclarified"

        self.link = SETTINGS["base_url"] + self.listing_code.find("a").attrs["href"]
        self.price = (
            self.listing_code.find("p", {"data-testid": "ad-price"}).text.split("zł")[0]
            + "PLN"
        )
        self.date = (
            self.listing_code.find("p", {"data-testid": "location-date"})
            .text.split("-")[1]
            .strip()
        )
        self.location = (
            self.listing_code.find("p", {"data-testid": "location-date"})
            .text.split("-")[0]
            .strip()
        )


class Listings:
    def __init__(self) -> None:
        self.val_offers = []
        self.unval_offers = []
        self.desired_keyword = SETTINGS["desired_keyword"]
        self.undesired_keywords = SETTINGS["undesired_keywords"]

    def _check_keywords(self, ls_name):  # checks whether listing name match keywords
        for word in self.desired_keyword:
            if word in ls_name:
                for un_word in self.undesired_keywords:
                    if un_word in ls_name:
                        return False
                return True
        return False

    def add_unv_listings(self, listings):
        self.unval_offers = [Listing(ls) for ls in listings]

    def add_val_listing(self, listing):
        listing._create_full_data()
        self.val_offers.append(listing)

    def validate_listings(self):
        for offer in self.unval_offers:
            if not offer._is_highlighted() and self._check_keywords(
                offer.listing_name.lower()
            ):
                self.add_val_listing(offer)

    def sort_listings_by_price(self):
        locale.setlocale(locale.LC_ALL, "")
        self.val_offers.sort(key=lambda x: locale.atof(x.price.split(" ")[0]))

    def save_listings_to_csv(self):
        with open(LOG_NAME, "w", newline="", encoding="utf-8") as csvfile:
            keys = [
                "listing_name",
                "condition",
                "link",
                "price",
                "date",
                "location",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            for data in self.val_offers:
                writer.writerow(data.__dict__)

    def open_new_listings(self):
        os.system(LOG_NAME)


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


def main():

    scraper = OlxScraper()
    listings = Listings()
    scraper.start_session()
    scraper.get_all_pages()
    for p in range(scraper.page_number):
        listings.add_unv_listings(scraper.get_listings_from_page(p))
        listings.validate_listings()
        listings.sort_listings_by_price()
    listings.save_listings_to_csv()
    listings.open_new_listings()


if __name__ == "__main__":
    main()
