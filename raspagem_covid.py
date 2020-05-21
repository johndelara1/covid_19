#!/usr/bin/python
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from time import sleep

class Raspagem:
    def __init__(self, driver):
        self.driver = driver
        self.url_site = f'https://covid.saude.gov.br/'
        ff.get(self.url_site)
        self.botao = ff.find_element_by_xpath(
            '/html/body/app-root/ion-app/ion-router-outlet/app-home/ion-content/div[1]/div[2]/ion-button'
        )
        self.botao.click()
        sleep(10)
ff = webdriver.Chrome()
raspagem = Raspagem(ff)
ff.quit()
