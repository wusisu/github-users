# -*- coding: utf-8 -*-
import threading
import time
from queue import Queue, Empty

import logging
import requests
from requests import ConnectTimeout, ReadTimeout, Timeout
from requests.exceptions import ProxyError, ChunkedEncodingError

from scrapyspider.common.persistence import Mongoing

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def get_nowait_none_for_empty(queue):
    try:
        return queue.get_nowait()
    except Empty:
        return None


def runner(queue):
    proxy_item = get_nowait_none_for_empty(queue)
    while proxy_item:
        url = proxy_item['url']
        succeed = False
        delay = 3600 * 2
        content = None
        exception = None
        error = None
        try:
            response = requests.get('http://myip.ipip.net', proxies={'http': url, 'https': url}, timeout=20)
            if response.status_code == 200 and response.text and response.text.startswith('当前 '):
                succeed = True
                content = response.text
            elif response.status_code == 429:
                delay = 3600 * 1
                error = content
                # logger.info('%s status: %s content: %s' % (url, response.status_code, response.text))
        except Timeout:
            exception = Timeout.__name__
            error = 'timeout'
        except ProxyError:
            exception = ProxyError.__name__
            error = 'proxy error'
        except ChunkedEncodingError:
            exception = ChunkedEncodingError.__name__
        except Exception as e:
            exception = e.__name__

        object_id = proxy_item['_id']
        Mongoing.db().proxies.update_one({'_id': object_id}, {
            '$set': {
                'next_check_time': time.time() + delay,
                'connectability': succeed,
                'content': content,
                'exception': exception,
                'error': error
            }
        })
        logger.info("%s %s" % (url, succeed))

        proxy_item = get_nowait_none_for_empty(queue)

    logger.info("exiting...")


if __name__ == '__main__':
    logger.info("process started")
    collection = Mongoing.db().proxies
    to_be_checked = collection.find({
        '$or': [
            {'next_check_time': None},
            {'next_check_time': {'$lt': time.time()}}
        ]
    })
    queue = Queue()
    for item in to_be_checked:
        queue.put(item)
    # runner(queue)
    for i in range(30):
        t = threading.Thread(target=runner, args=(queue,))
        t.start()
