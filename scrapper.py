from __future__ import unicode_literals

import time
import orm
import datetime
import logging
import random
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

    def _quit(self):
        if self.driver:
            pass
            # self.driver.close()

    def scrap_dr(self, nb_col, prov=''):
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
            infos = None
        finally:
            self._quit()

        return infos

    def scrap_results(self):
        tr = 1
        while True:
            nb_co = self._get_field(self.meta['elems']['iter_co'].format(tr))
            if nb_co:
                yield str(nb_co.text)
            else:
                break
            tr += 1

    def scrap_dr_by_name(self, co_colegiado, no_nombre, no_apellido1, no_apellido2):
        new_co_colegiado = None
        try:
            self.driver.get(self.meta['url'])

            nombre_field = self._get_field(self.meta['elems']['nombre_field'])
            app1_field = self._get_field(self.meta['elems']['app1_field'])
            btn_buscar = self._get_field(self.meta['elems']['busc_btn'])

            nombre_field.send_keys(no_nombre.decode('latin_1'))
            app1_field.send_keys(no_apellido1.decode('latin_1'))
            btn_buscar.click()

            try:

                for cod in self.scrap_results():
                    if co_colegiado[4:] == cod[4:]:
                        new_co_colegiado = cod
                        break
            except:
                logging.info('Could not find any other register for co_colegiado = {}'
                             .format(co_colegiado))

        except Exception as err:
            raise Exception('Error occured while `scrap_dr_by_name` to {}. '
                            'Possibly Conection Problem'.format(co_colegiado))
        finally:
            self._quit()

        return new_co_colegiado


class Manager(object):
    def __init__(self, ds, spr, conf):
        self.ds = ds
        self.spr = spr
        self.conf = conf

    def next_dr_check(self, nb_doctors):
        for _ in range(nb_doctors):
            yield self.ds.next_dr_check()

    def check(self, dr):
        if self.spr.scrap_dr(dr.co_colegiado):
            dr.dt_last_check = datetime.datetime.utcnow()
            logging.info('{} is still active'.format(dr.co_colegiado))
            self.ds.update(dr)
        else:
            new_co_colegiado = self.spr.scrap_dr_by_name(
                dr.co_colegiado, dr.no_nombre, dr.no_apellido1, dr.no_apellido2
            )
            if new_co_colegiado:
                logging.info('New co_colegiado found for {}: {}'.format(
                    dr.co_colegiado, new_co_colegiado
                ))

                dr.fl_estado = 4
                dr.dt_modi_reg = datetime.datetime.utcnow()
                dr.dt_last_check = datetime.datetime.utcnow()
                dr.no_modi_usr = 'CRAWLER'
                self.ds.update(dr)
                self.ds.insert_transient(
                    dr, new_co_colegiado, datetime.datetime.utcnow()
                )
            else:
                logging.info('{} is not active'.format(dr.co_colegiado))
                dr.fl_estado = 3
                dr.dt_modi_reg = datetime.datetime.utcnow()
                dr.dt_last_check = datetime.datetime.utcnow()
                dr.no_modi_usr = 'CRAWLER'
                self.ds.update(dr)

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
            attempts = [str(n + int(last_nb_col)) for n in range(
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
        no_nombre, no_apellido1, no_apellido2 = None, None, None
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
                dt_creat_reg=datetime.datetime.utcnow(),
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

    def get_doctors_range(self):
        return self.conf['nb_checks']

    def check_wait(self):
        time_to_sleep = random_distr(sorted(
            self.conf['wait_check'].items(), key=lambda x: x[1]
        ))
        logging.info('Random wait: {}s'.format(time_to_sleep))
        time.sleep(time_to_sleep)


def random_distr(l):
    r = random.uniform(0, 1)
    s = 0
    for item, prob in l:
        s += prob
        if s >= r:
            return float(item)
    return float(item)