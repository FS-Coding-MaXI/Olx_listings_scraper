import requests
from bs4 import BeautifulSoup
import re
import locale
import csv
import time

base_url = "https://www.olx.pl"
pencil_search = "/oferty/q-apple-pencil/"
log_name = (
    "olx_scraper_"
    + "-".join((time.strftime("%D_%H-%M-%S", time.localtime())).split("/"))
    + ".csv"
)

upper_limit = 400
lower_limit = 199
filters1 = f"?search%5Bfilter_float_price:from%5D={lower_limit}&search%5Bfilter_float_price:to%5D={upper_limit}"
params = {
    "search[filter_float_price:from]": 149,
    "search[filter_float_price:to]": 450,
}

s = requests.Session()
print(base_url + pencil_search + filters1)
res = s.get(base_url + pencil_search, params=params)
print(res.url)
html = res.content
soup = BeautifulSoup(html, "lxml")
number_of_pages = int(
    soup.find_all("li", {"data-testid": "pagination-list-item"})[-1].text
)

json_format = []

for x in range(number_of_pages):

    page = f"page={x+1}"
    params["page"] = x + 1
    print(base_url + pencil_search + page + filters1)
    res = s.get(base_url + pencil_search, params=params)
    print(res.url)
    html = res.content

    soup = BeautifulSoup(html, "lxml")

    listings = soup.find(
        "div", class_=re.compile(r"listing-grid-container.*")
    ).find_all("div", {"data-cy": "l-card"})

    def keywords_check(ls_name) -> bool:
        wanted_keywords = [
            "apple pencil",
            "pencil",
            "1 gen",
            "1. gen",
            "2 gen",
            "2. gen",
            "rysik ipad",
            "rysik",
        ]
        unwanted_keywords = [
            "etui",
            "logitech",
            "zagg",
            "stylus",
            "ładowarka",
            "obudowa",
            "shield",
        ]
        for word in wanted_keywords:
            if word in ls_name:
                for un_word in unwanted_keywords:
                    if un_word in ls_name:
                        return False
                return True
        return False

    for listing in listings:
        listing_name = listing.find("h6").text
        if (
            listing.find("div", {"data-testid": "adCard-featured"}) is None
        ) and keywords_check(listing_name.lower()):
            json_format.append(
                {
                    "listing_name": listing_name,
                    "condition": listing.find(
                        "span", {"title": re.compile(r".*")}
                    ).text,
                    "link": base_url + listing.find("a").attrs["href"],
                    "price": listing.find("p", {"data-testid": "ad-price"}).text.split(
                        "zł"
                    )[0]
                    + "PLN",
                    "date": listing.find("p", {"data-testid": "location-date"})
                    .text.split("-")[1]
                    .strip(),
                    "location": listing.find("p", {"data-testid": "location-date"})
                    .text.split("-")[0]
                    .strip(),
                }
            )


locale.setlocale(locale.LC_ALL, "")
json_format.sort(key=lambda x: locale.atof(x["price"].split(" ")[0]))

# for json in json_format:
#     pprint(json)

with open(log_name, "w", newline="", encoding="utf-8") as csvfile:
    keys = ["listing_name", "condition", "link", "price", "date", "location"]
    writer = csv.DictWriter(csvfile, fieldnames=keys, extrasaction="ignore")
    writer.writeheader()
    for json in json_format:
        writer.writerow(json)
