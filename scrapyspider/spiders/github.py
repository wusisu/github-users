# -*- coding: utf-8 -*-
import json

import requests
import scrapy


class GithubSpider(scrapy.Spider):
    name = 'github'
    allowed_domains = ['api.github.com']
    start_urls = ['https://api.github.com/users/willin']

    def parse(self, response):
        data = json.loads(response.body_as_unicode())
        login = data['login']
        print login
        for request in self.handle_user_for_follow(login):
            yield request

    # find user by following and followers
    def handle_user_for_follow(self, login):
        if not login:
            return
        yield scrapy.Request('https://api.github.com/users/' + login + '/followers?', callback=self.parse_follow)
        yield scrapy.Request('https://api.github.com/users/' + login + '/following?', callback=self.parse_follow)

    def fuck_the_user(self, login):
        yield scrapy.Request('https://api.github.com/users/' + login, callback=self.parse)

    def parse_follow(self, response):
        data = json.loads(response.body_as_unicode())
        for user in data:
            yield self.fuck_the_user(user['login'])
        # next pages
        links = response.headers['Link']
        if links:
            links = requests.utils.parse_header_links(links.rstrip('>').replace('>,<', ',<'))
            for link in links:
                if link['rel'] == 'next':
                    if link['url']:
                        yield scrapy.Request(link['url'], self.parse_follow)