import json

import requests
import scrapy

from scrapyspider.items import UserItem, FollowItem


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['api.github.com']
    start_urls = ['https://api.github.com/users/willin']

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        login = data['login']
        user = UserItem(login=login, data=data)
        yield user
        for request in self.handle_user_for_follow(login):
            yield request

    # find user by following and followers
    def handle_user_for_follow(self, login):
        if not login:
            return
        yield scrapy.Request('https://api.github.com/users/' + login + '/followers?', callback=self.parse_follow)
        yield scrapy.Request('https://api.github.com/users/' + login + '/following?', callback=self.parse_follow)

    def fuck_the_user(self, login):
        return scrapy.Request('https://api.github.com/users/' + login, callback=self.parse)

    def parse_follow(self, response):
        url = response.url.split('?')[0]
        data = json.loads(response.body_as_unicode())
        category = None
        login = url.split('/')[-2]
        items = FollowItem(login=login)
        if url.endswith('followers'):
            category = 'followers'
            items['followers_login'] = data
        elif url.endswith('following'):
            category = 'following'
            items['following_login'] = data
        if not category or not login:
            raise Exception("no accepted %s" % url)
        yield items
        for user in data:
            pass
            # yield self.fuck_the_user(user['login'])
        return
        # next pages
        if 'Link' in response.headers and response.headers['Link']:
            links = requests.utils.parse_header_links(response.headers['Link'].rstrip('>').replace('>,<', ',<'))
            for link in links:
                if link['rel'] == 'next':
                    if link['url']:
                        yield scrapy.Request(link['url'], self.parse_follow)
