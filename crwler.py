import argparse
import threading
import json
import codecs
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

    def scrap_dr(self, nb_col):
        self.driver.get(self.meta['url'])

        nb_col_field = self._get_field(self.meta['elems']['nb_col_field'])
        btn_buscar = self._get_field(self.meta['elems']['busc_btn'])

        nb_col_field.send_keys(nb_col)
        btn_buscar.click()
        nombre_res = self._get_field(self.meta['elems']['nombre_res'])

        return nombre_res.text



class Crawler(threading.Thread):

    def __init__(self, meta):
        threading.Thread.__init__(self)
        self.meta = meta
        self.scrapper = SiteScrapper(meta['scrapper'])

    def run(self):
        print self.scrapper.scrap_dr(nb_col='282835349')

def main(args):
    props = 'resources/properties.json'
    with codecs.open(props, 'r', encoding='utf-8') as f:
        crwler = Crawler(json.loads(f.read()))
    crwler.start()

def parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())