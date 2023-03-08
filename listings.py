from settings import SETTINGS, LOG_PATH
from single_listing import Listing
import locale
import os
import csv


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
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as csvfile:
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
        os.system(LOG_PATH)
