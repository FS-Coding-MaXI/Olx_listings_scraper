import json, time
from os import path

# loads settings for the scraper such as
# keywords
# filters (price limits)
# products we look for
# base olx url

OLX_SETTINGS = json.load(open("olx_settings.json"))

# generates name for the log of the one session of running

LOG_PATH = path.join(
    "logs",
    "olx_scraper_"
    + "-".join((time.strftime("%D_%H-%M-%S", time.localtime())).split("/"))
    + ".csv",
)

# keeps up gcp settings, NEEDED ONLY IF YOU WANT TO DEPLOY IT ON SERVER
