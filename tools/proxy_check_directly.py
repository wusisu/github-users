# -*- coding: utf-8 -*-
from queue import Queue, Empty
from threading import Thread
from time import sleep

import logging
import requests
from requests import Timeout
from requests.exceptions import ProxyError, ChunkedEncodingError

logging.basicConfig(format="%(threadName)s:%(message)s")

q = Queue(10000)
got = Queue()
all = []


def run():
    while True:
        try:
            index, url = q.get_nowait()
        except Empty:
            return

        exception = None
        error = None
        succeed = False
        try:
            response = requests.get('http://myip.ipip.net', proxies={'http': url, 'https': url}, timeout=20)
            if response.status_code == 200 and response.text and response.text.startswith('当前 '):
                logging.info(index, 'succeed for', url)
                got.put_nowait(url)
                succeed = True
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
        if not succeed:
            logging.info(index, 'failed for', url, exception, error)


def collect():
    with open('../data/check.txt', 'a') as wfp:
        while not got.empty():
            u = got.get_nowait()
            wfp.write(u)
            wfp.write('\n')


if __name__ == '__main__':
    with open('../data/proxy.txt', 'r') as fp:
        urls = [line.replace("\n", "").strip() for line in fp.readlines()]
        urls = list(filter(lambda x: x, urls))
        for idx, u in enumerate(urls):
            q.put_nowait((idx, u))
        for i in range(20):
            t = Thread(target=run, name='wtt-' + str(i))
            t.start()
        while not q.empty():
            collect()
            sleep(10)
        collect()
