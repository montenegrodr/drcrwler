from __future__ import unicode_literals

import logging
import warnings
import argparse
import json
import codecs
import threading
from checker import Checker
from scrapper import SiteScrapper
from scrapper import Manager
from orm import Dataset


class Crawler(threading.Thread):
    def __init__(self, mgr):
        threading.Thread.__init__(self)
        self.mgr = mgr

    def run(self):
        logging.info('[crawler] Crawl begins here')
        while True:
            for p in self.mgr.prov_range():
                try:
                    logging.info('[crawler] Starting search for provincia {}'.format(p))
                    for dr in self.mgr.get_next_dr(p):
                        logging.info('[crawler] Found Dr. nb_col: {}'.format(dr[u'nb_col']))
                        self.mgr.insert(dr)
                    logging.info('[crawler] No more Dr. found for provincia {}'.format(p))
                except Exception as err:
                    logging.error('Exception: {}'.format(err))
                finally:
                    self.mgr.long_wait('[crawler]')


def main(args):
    with codecs.open(args.props, 'r', encoding='utf-8') as f:
        meta = json.loads(f.read())

    logging.info('Creating dataset instance')
    ds = Dataset(meta['database'])

    logging.info('Creating scrapper instance')
    spr1 = SiteScrapper(meta['scrapper'], phantomjs='phantomjs1')
    spr2 = SiteScrapper(meta['scrapper'], phantomjs='phantomjs2')

    logging.info('Creating manager instance')
    mgr1 = Manager(ds, spr1, meta['conf'])
    mgr2 = Manager(ds, spr2, meta['conf'])

    threads = []
    crawler = Crawler(mgr1)
    crawler.daemon = True
    crawler.start()
    threads.append(crawler)

    checker = Checker(mgr2)
    checker.daemon = True
    checker.start()
    threads.append(checker)

    # for th in threads:
    #     th.join()
    while True:
        pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--props', default='resources/properties.json')
    return parser.parse_args()

if __name__ == '__main__':
    warnings.simplefilter('ignore')
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)
    main(parse_args())
