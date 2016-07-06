from __future__ import unicode_literals

import logging
import codecs
import argparse
import json
import warnings
import threading
from orm import Dataset
from scrapper import SiteScrapper
from scrapper import Manager


class Checker(threading.Thread):
    def __init__(self, mgr):
        threading.Thread.__init__(self)
        self.mgr = mgr

    def run(self):
        logging.info('[checker] Doctor check begins here')
        nb_doctors = self.mgr.get_doctors_range()

        while True:
            try:
                logging.info('[checker] Doctors batch: {}'.format(nb_doctors))
                for nb_dr, dr in enumerate(self.mgr.next_dr_check(nb_doctors)):
                    logging.info('[checker] Checking Dr. nb_col: {} {}/{}'.format(
                        dr.co_colegiado, nb_dr+1, nb_doctors
                    ))
                    self.mgr.check(dr)
                    self.mgr.short_wait()
                logging.info('[checker] Batch ended. Waiting')
                self.mgr.check_wait()
            except Exception as err:
                logging.error('Exception: {}'.format(err))
            finally:
                self.mgr.long_wait('[checker]')


def main(args):
    with codecs.open(args.props, 'r', encoding='utf-8') as f:
        meta = json.loads(f.read())

    logging.info('[checker] Creating dataset instance')
    ds = Dataset(meta['database'])

    logging.info('[checker] Creating scrapper instance')
    spr = SiteScrapper(meta['scrapper'])

    logging.info('[checker] Creating manager instance')
    mgr = Manager(ds, spr, meta['conf'])

    Checker(mgr).start()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--props', default='resources/properties.json')
    return parser.parse_args()


if __name__=='__main__':
    warnings.simplefilter('ignore')
    logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO)
    main(parse_args())