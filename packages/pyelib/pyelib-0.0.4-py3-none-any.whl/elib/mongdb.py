import pymongo


class MongoDB:

    def __init__(self, url, database_name, collection_name):
        self.client = pymongo.MongoClient(url)
        self.database = self.client[database_name]
        self.collection = self.database[collection_name]

    def insert_one(self, document):
        return self.collection.insert_one(document)

    def insert_many(self, documents):
        return self.collection.insert_many(documents)

    def find_one(self, filters=None, *args, **kwargs):
        return self.collection.find_one(filters, *args, **kwargs)

    def find_many(self, filters=None, *args, **kwargs):
        return self.collection.find(filters, *args, **kwargs)

    def update_one(self, filters, update, *args, **kwargs):
        return self.collection.update_one(filters, update, *args, **kwargs)

    def update_many(self, filters, update, *args, **kwargs):
        return self.collection.update_many(filters, update, *args, **kwargs)

    def delete_one(self, filters, *args, **kwargs):
        return self.collection.delete_one(filters, *args, **kwargs)

    def delete_many(self, filters, *args, **kwargs):
        return self.collection.delete_many(filters, *args, **kwargs)
