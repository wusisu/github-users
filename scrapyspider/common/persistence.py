# -*- coding: utf-8 -*-
import pymongo

from scrapyspider import settings


class Mongoing(object):
    _client = None
    _db = settings.MONGO_DB

    @staticmethod
    def new_instance():
        return pymongo.MongoClient(settings.MONGO_URL)

    @classmethod
    def client(cls):
        if not cls._client:
            cls._client = Mongoing.new_instance()
        return cls._client

    @classmethod
    def db(cls):
        return cls.client()[cls._db]

if __name__=='__main__':
    items = Mongoing.db()['items']
    print(list(items.find({})))
