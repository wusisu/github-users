import time

import scrapy
import twisted
from requests import RequestException

from scrapyspider.common.persistence import Mongoing


class ProxyMiddleware(object):
    def find_proxy(self):
        return Mongoing.db().proxies.find_one({
            'connectability': True,
            '$or': [
                {'gh_reset': {'$exists': False}},
                {'gh_remaining': {'$exists': False}},
                {'gh_reset': {'$lt': time.time()}},
                {'gh_remaining': {'$gt': 3}}
            ]
        })
        pass

    def process_request(self, request, spider):
        proxy = self.find_proxy()
        if not proxy:
            spider.logger.info('No more proxy, waiting...')
            time.sleep(60)
            return request
        spider.logger.debug('using proxy: %s' % proxy)
        request.meta['proxy'] = "http://%s" % proxy['url']
        request.meta['proxy_id'] = proxy['_id']
        request.meta['download_timeout'] = 10
        # if proxy['user_pass'] is not None:
        #     request.meta['proxy'] = "http://%s" % proxy['ip_port']
        #     encoded_user_pass = base64.encodestring(proxy['user_pass'])
        #     request.headers['Proxy-Authorization'] = 'Basic ' + encoded_user_pass
        #     print("**************ProxyMiddleware have pass************" + proxy['ip_port'])
        # else:
        #     print("**************ProxyMiddleware no pass************" + proxy['ip_port'])
        #     request.meta['proxy'] = "http://%s" % proxy['ip_port']

    def process_response(self, request, response, spider):
        headers = response.headers
        if 'X-RateLimit-Remaining' in headers and 'X-RateLimit-Reset' in headers:
            remaining = headers['X-RateLimit-Remaining']
            reset = headers['X-RateLimit-Reset']
            proxy_id = request.meta['proxy_id']
            if remaining and reset and proxy_id:
                spider.logger.debug("Remaining %s, reset in %s, proxy_id %s" %
                                    (remaining, int(reset) - time.time(), proxy_id))
                Mongoing.db().proxies.update_one({'_id': proxy_id}, {
                    '$set': {
                        'gh_reset': int(reset),
                        'gh_remaining': int(remaining)
                    }
                })
        return response

    def process_exception(self, request, exception, spider):
        print('process_exception in proxy')
        re_schedule = False
        failed_reason = None

        if isinstance(exception, twisted.internet.error.TimeoutError):
            failed_reason = twisted.internet.error.TimeoutError.__name__
            re_schedule = True
        elif isinstance(exception, scrapy.core.downloader.handlers.http11.TunnelError):
            failed_reason = scrapy.core.downloader.handlers.http11.TunnelError.__name__
            re_schedule = True
        else:
            spider.logger.debug('exception: %s %s' % (str(type(exception)), str(exception)))

        if failed_reason:
            proxy_id = request.meta['proxy_id']
            if not proxy_id:
                spider.logger.debug('No proxy id found')
            else:
                spider.logger.info('updating connectability for id %s' % proxy_id)
                Mongoing.db().proxies.update_one({'_id': proxy_id}, {
                    '$set': {
                        'connectability': False,
                        'exception': failed_reason
                    }
                })
        if re_schedule:
            copy_req = request.copy()
            copy_req.meta['retry_times'] = 0
            spider.logger.info('rescheduler request: %s' % request.url)
            return copy_req


if __name__ == '__main__':
    print(ProxyMiddleware().find_proxy())
