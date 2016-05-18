from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

browser = webdriver.PhantomJS('phantomjs-2.1.1-linux-x86_64/bin/phantomjs')
# browser = webdriver.Firefox()


browser.get('http://cgcom-interno.vuds-omc.es/RegistroMedicos/PUBBusquedaPublica_busqueda.action')

nb_col_id = 'numeroColegiado'
name_id = 'Nombre'
app1_id = 'Apellido1'
btn_xpath = '/html/body/div/div/div/form[2]/table/tbody/tr[4]/td/input'

timeout = 5

nb_col_elem = WebDriverWait(browser, timeout).until(
        lambda driver : driver.find_element_by_id(nb_col_id)
)

name_elem = WebDriverWait(browser, timeout).until(
        lambda driver : driver.find_element_by_id(name_id)
)


nb_col_elem.send_keys('282835348')
app1_elem = WebDriverWait(browser, timeout).until(
        lambda driver : driver.find_element_by_id(app1_id)
)

btn_elem = WebDriverWait(browser, timeout).until(
        lambda driver : driver.find_element_by_xpath(btn_xpath)
)
btn_elem.click()


name_td = WebDriverWait(browser, timeout).until(
        lambda driver : driver.find_element_by_xpath('/html/body/div/div/div/form[2]/div/table/tbody/tr/td[2]')
)

print name_td.text
