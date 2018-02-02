# -*- coding: utf-8 -*-
from pymongo.errors import BulkWriteError

from scrapyspider.common.persistence import Mongoing

if __name__ == '__main__':
    collection = Mongoing.db().proxies
    count_before = collection.count()
    count_adding = 0
    with open('../data/proxy.txt', 'r') as fp:
        urls = [line.replace("\n", "").strip() for line in fp.readlines()]
        urls = list(filter(lambda x: x, urls))
        count_adding = len(urls)
        items = [{'url': url} for url in urls]
        try:
            collection.insert_many(items, ordered=False)
        except BulkWriteError:
            pass
    count_after = collection.count()
    print("db count from %s to %s, try to insert %s items, actually %s added." %
          (count_before, count_after, count_adding, count_after - count_before))