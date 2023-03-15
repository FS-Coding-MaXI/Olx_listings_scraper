from settings import OLX_SETTINGS
import re
from datetime import datetime


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

    def _format_date(self):
        date = (
            self.listing_code.find("p", {"data-testid": "location-date"})
            .text.split("-")[-1]
            .strip()
        )
        if ":" in date:
            return datetime.today().strftime("%B %d, %Y") + f' {date.split(" ")[-1]}'
        if len(date.split(" ")) > 4:
            date = " ".join(date.split(" ")[2:])
        lookup_table = {
            "stycznia": "January",
            "lutego": "February",
            "marca": "March",
            "kwietnia": "April",
            "maja": "May",
            "czerwca": "June",
            "lipca": "July",
            "sierpnia": "August",
            "września": "September",
            "października": "October",
            "listopada": "November",
            "grudnia": "December",
        }
        for k, v in lookup_table.items():
            date = date.replace(k, v)

        return datetime.strptime(date, "%d %B %Y").strftime("%B %d, %Y")

    def _create_full_data(self):  # fetches validated listing data
        try:
            self.condition = self.listing_code.find(
                "span", {"title": re.compile(r".*")}
            ).text
        except AttributeError:  # if there isn't such as span
            self.condition = "Unclarified"
        self.sent2discord = False
        self.link = OLX_SETTINGS["base_url"] + self.listing_code.find("a").attrs["href"]
        self.price = "".join(
            [
                z
                for z in self.listing_code.find("p", {"data-testid": "ad-price"}).text
                if z.isnumeric()
            ]
        )
        self.date = self._format_date()
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
