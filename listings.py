from settings import OLX_SETTINGS, LOG_PATH
from single_listing import Listing
from locale import atof
import os
import csv


class Listings:
    def __init__(self) -> None:
        self.val_offers = []
        self.unval_offers = []
        self.today_listings_links = []
        self.desired_keyword = OLX_SETTINGS["possible_keywords"]
        self.undesired_keywords = OLX_SETTINGS["undesired_keywords"]

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

    def validate_listings(self, first_run=True):
        for offer in self.unval_offers:
            if (
                not offer._is_highlighted()
                and self._check_keywords(offer.listing_name.lower())
                and not any(
                    ls_name.__dict__["listing_name"] == offer.listing_name
                    for ls_name in self.val_offers
                )
            ):
                self.add_val_listing(offer)
                if ":" in offer.date and first_run:
                    self.today_listings_links.append(offer.link)

    def if_new_listing(self):
        return len([z for z in self.val_offers if ":" in z.date]) > len(
            self.today_listings_links
        )

    def find_new_listing(self):
        listings_to_check = [z for z in self.val_offers if ":" in z.date]
        new_ls = [
            ls for ls in listings_to_check if ls.link not in self.today_listings_links
        ][0]
        self.today_listings_links.append(new_ls.link)
        return new_ls

    def sort_listings_by_price(self):
        self.val_offers.sort(key=lambda x: atof(x.price))

    def sort_listings_by_key_priority(self):
        counter = 0
        new_list = []
        for offer in self.val_offers:
            satisfy_conditions = False
            for word in OLX_SETTINGS["desired_keywords"]:
                if word in offer.listing_name.lower():
                    new_list.insert(counter, offer)
                    counter += 1
                    satisfy_conditions = True
                    break
            if not satisfy_conditions:
                new_list.append(offer)
        self.val_offers = new_list

    def listings_to_csv(self):
        with open(LOG_PATH, "w", newline="", encoding="utf-8") as csvfile:
            keys = [
                "listing_name",
                "condition",
                "date",
                "negotiable",
                "price",
                "link",
                "location",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            for data in self.val_offers:
                writer.writerow(data.__dict__)

    def open_new_listings_csv(self):
        os.system(LOG_PATH)
