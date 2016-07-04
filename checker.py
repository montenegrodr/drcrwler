from __future__ import unicode_literals

import logging
import codecs
import argparse
import json
import warnings
from orm import Dataset
from scrapper import SiteScrapper
from scrapper import Manager


def start_checker(mgr):

    logging.info('Doctor check begins here')
    nb_doctors = mgr.get_doctors_range()

    while True:
        try:
            logging.info('Doctors batch: {}'.format(nb_doctors))
            for nb_dr, dr in enumerate(mgr.next_dr_check(nb_doctors)):
                logging.info('Checking Dr. nb_col: {} {}/{}'.format(
                    dr.co_colegiado, nb_dr+1, nb_doctors
                ))
                mgr.check(dr)
                mgr.short_wait()
            logging.info('Batch ended. Waiting')
            mgr.check_wait()
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

    start_checker(mgr)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--props', default='resources/properties.json')
    return parser.parse_args()


if __name__=='__main__':
    warnings.simplefilter('ignore')
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)
    main(parse_args())