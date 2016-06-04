from __future__ import unicode_literals

import logging
import warnings
import argparse
import json
import codecs
import time
import orm
import datetime
from orm import Dataset
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait


class SiteScrapper(object):

    def __init__(self, meta):
        self.meta = meta
        self.wait = meta['wait']
        self.driver = self._get_browser()

    def _get_browser(self):
        if self.meta['browser'] == 'phantomjs':
            return webdriver.PhantomJS(self.meta['phantomjs'])
        elif self.meta['browser'] == 'firefox':
            return webdriver.Firefox()

    def _get_field(self, xpath):
        return WebDriverWait(self.driver, self.wait).until(
            lambda driver : driver.find_element_by_xpath(xpath)
        )

    def _refresh(self):
        self.driver.refresh()

    def scrap_dr(self, nb_col, prov):
        infos = None

        try:
            self.driver.get(self.meta['url'])

            nb_col_field = self._get_field(self.meta['elems']['nb_col_field'])
            btn_buscar = self._get_field(self.meta['elems']['busc_btn'])

            nb_col_field.send_keys(nb_col)
            btn_buscar.click()

            plus_btn = self._get_field(self.meta['elems']['plus_btn'])

            plus_btn.click()

            infos = {
                'nb_col': nb_col,
                'nombre': self._get_field(
                        self.meta['elems']['nombre']
                ).text,
                'co_provincia_cole': str(prov).zfill(2),
                'provincia_cole': self._get_field(
                        self.meta['elems']['provincia_cole']
                ).text,
                'especialidad': self._get_field(
                        self.meta['elems']['especialidad']
                ).text,
                'estado_cole': self._get_field(
                        self.meta['elems']['estado_cole']
                ).text,
                'direccion': self._get_field(
                        self.meta['elems']['direccion']
                ).text,
            }
        except Exception:
            logging.error('Any information was found for '
                          'nb_col = {} and prov = {}'.format(nb_col, prov))
        return infos


class Manager(object):
    def __init__(self, ds, spr, conf):
        self.ds = ds
        self.spr = spr
        self.conf = conf

    def get_next_dr(self, prov):
        dr = True
        last_scrap = None
        while dr:
            while True:
                if last_scrap and \
                                (datetime.datetime.now() - last_scrap).seconds < self.conf['min_req_time']:
                    logging.info('Min request time not achieved')
                    self.short_wait()
                    continue
                break

            last_nb_col = self.ds.get_last_nb_col(prov)
            attempts = [str(n + last_nb_col) for n in range(
                    1, self.conf['attempts'] + 1
            )]
            dr = None
            for a in attempts:
                a_str = str(a).zfill(9)
                last_scrap = datetime.datetime.now()
                dr = self.spr.scrap_dr(a_str, prov)
                if dr:
                    yield dr
                    break
                self.short_wait()

    def insert(self, dr):
        for i, nom in enumerate(dr[u'nombre'].split()):
            if i == 0:
                no_nombre = nom
            elif i == 1:
                no_apellido1 = nom
            elif i == 2:
                no_apellido2 = ' '.join(dr[u'nombre'].split()[2:])
                break
        co_provincia_cole = None
        dr_orm = orm.Doctor(
                co_colegiado=dr[u'nb_col'],
                no_nombre=no_nombre,
                no_apellido1=no_apellido1,
                no_apellido2=no_apellido2,
                co_provincia_cole=co_provincia_cole,
                no_provincia_cole=dr[u'provincia_cole'],
                no_especialidad_list=dr[u'especialidad'],
                fl_estado=1,
                no_crea_usr='CRAWLER',
                fl_off_reg=0
        )
        self.ds.insert(dr_orm)

    def prov_range(self):
        return range(self.conf['prov0'], self.conf['provf'])

    def long_wait(self):
        logging.info('Long wait: {} s'.format(self.conf['long_wait']))
        time.sleep(self.conf['long_wait'])

    def short_wait(self):
        logging.info('Short wait: {} s'.format(self.conf['short_wait']))
        time.sleep(self.conf['short_wait'])


def start_crawler(mgr):

    logging.info('Crawl begins here')
    while True:
        try:
            for p in mgr.prov_range():
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