# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class UserItem(scrapy.Item):
    # define the fields for your item here like:
    login = scrapy.Field()
    data = scrapy.Field()
    data_with_email = scrapy.Field()
    following_ok = scrapy.Field()
    followers_ok = scrapy.Field()


class FollowItem(scrapy.Item):
    # define the fields for your item here like:
    login = scrapy.Field()
    following_login = scrapy.Field()
    followers_login = scrapy.Field()
