import pymongo
from single_listing import Listing
import asyncio

class Database(pymongo.MongoClient):
    def __init__(self, user, password):
        super().__init__(
            f"mongodb+srv://{user}:{password}@olx-scrapper.hpl6bsu.mongodb.net/?retryWrites=true&w=majority"
        )

        self.db = self["olx-scrapper"]

        self.listing_collection = self.db["listings"]

    async def ifExists(self, listing: Listing):
        if self.listing_collection.find({'link': listing.link}).count() > 0:
            return True
        return False
    
    async def add_listing(self, listing: Listing):
        self.listing_collection.insert_one(listing)
