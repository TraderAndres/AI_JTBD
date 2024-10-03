# mongo_manager.py
from pymongo import MongoClient

class MongoDBManager:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection_name = None

    def set_collection(self, collection_name):
        self.collection_name = collection_name

    def insert_entry(self, entry):
        if not self.collection_name:
            raise ValueError("Collection name is not set.")
        return self.db[self.collection_name].insert_one(entry).inserted_id

    def find_entry(self, query):
        if not self.collection_name:
            raise ValueError("Collection name is not set.")
        return self.db[self.collection_name].find_one(query)

    def update_entry(self, query, new_values):
        if not self.collection_name:
            raise ValueError("Collection name is not set.")
        return self.db[self.collection_name].update_one(query, {"$set": new_values})

    def delete_entry(self, query):
        if not self.collection_name:
            raise ValueError("Collection name is not set.")
        return self.db[self.collection_name].delete_one(query)

    def get_all_entries(self):
        if not self.collection_name:
            raise ValueError("Collection name is not set.")
        return list(self.db[self.collection_name].find())
