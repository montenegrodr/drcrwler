from __future__ import unicode_literals

import logging
import warnings
import argparse
import json
import codecs
from scrapper import SiteScrapper
from scrapper import Manager
from orm import Dataset


def start_crawler(mgr):

    logging.info('Crawl begins here')
    while True:
        for p in mgr.prov_range():
            try:
                logging.info('Starting search for provincia {}'.format(p))
                for dr in mgr.get_next_dr(p):
                    logging.info('Found Dr. nb_col: {}'.format(dr[u'nb_col']))
                    mgr.insert(dr)
                logging.info('No more Dr. found for provincia {}'.format(p))
            except Exception as err:
                logging.error('Exception: {}'.format(err))
            finally:
                mgr.long_wait()


def main(args):
    with codecs.open(args.props, 'r', encoding='utf-8') as f:
        meta = json.loads(f.read())

    logging.info('Creating dataset instance')
    ds = Dataset(meta['database'])

    logging.info('Creating scrapper instance')
    spr = SiteScrapper(meta['scrapper'])

    logging.info('Creating manager instance')
    mgr = Manager(ds, spr, meta['conf'])

    start_crawler(mgr)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--props', default='resources/properties.json')
    return parser.parse_args()

if __name__ == '__main__':
    warnings.simplefilter('ignore')
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)
    main(parse_args())
