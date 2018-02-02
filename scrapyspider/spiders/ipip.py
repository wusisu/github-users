import scrapy


class GithubSpider(scrapy.Spider):
    name = 'ipip'
    allowed_domains = ['myip.ipip.net']
    start_urls = ['http://myip.ipip.net']

    counting = 0

    def parse(self, response):
        print(response.body.decode('utf8'))
        self.counting = self.counting + 1
        if self.counting > 2:
            return
        return scrapy.Request('http://myip.ipip.net', dont_filter=True)
