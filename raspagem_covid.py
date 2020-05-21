from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from time import sleep

ff = webdriver.Chrome()
url_site = f'https://covid.saude.gov.br/'
ff.get(url_site)
botao = ff.find_elements_by_css_selector(
    '[class="btn-white md button button-solid button-has-icon-only ion-activatable ion-focusable hydrated ion-activated"]'
)
#print(botao)
botao.click()
