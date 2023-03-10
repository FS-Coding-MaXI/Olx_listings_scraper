from settings import SETTINGS
import re


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
            .text.split("-")[-1]
            .strip()
        )
        self.location = (
            self.listing_code.find("p", {"data-testid": "location-date"})
            .text.split("-")[0]
            .strip()
        )
        try:  # if this span object exist, then it is negotiable
            len(
                self.listing_code.find("p", {"data-testid": "ad-price"})
                .find("span")
                .text
            )
            self.negotiable = "Yes"
        except AttributeError:
            self.negotiable = "No information"
        del self.listing_code

    # def __dict__(self):
    #     return {
    #         "name": self.listing_name,
    #         "condition": self.condition,
    #         "price": self.price,
    #         "date": self.date,
    #         "location": self.location,
    #         "link": self.link,
    #         "negotiable": self.negotiable
    #     }
