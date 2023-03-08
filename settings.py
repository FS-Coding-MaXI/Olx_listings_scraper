import json, time
from os import path

SETTINGS = json.load(open("settings.json"))

# loads settings for the scraper such as
# keywords
# filters (price limits)
# products we look for
# base olx url

LOG_PATH = path.join(
    "logs",
    "olx_scraper_"
    + "-".join((time.strftime("%D_%H-%M-%S", time.localtime())).split("/"))
    + ".csv",
)

# generates name for the log of the one session of running
