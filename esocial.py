# coding=utf8
# Selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options
# Basicos
from datetime import datetime
import time
import os,errno
import glob
# from sendmail import *
from unicodedata import normalize
import json
import re
# import requests

import cred

lCpf = cred.login['cpf']
lCod = cred.login['cod']
lPass = cred.login['pass']
lUrl = cred.login['url']

dirpath = os.path.dirname(os.path.realpath(__file__))
dirResultados = dirpath + '/resultados/'

#data e hora
h = datetime.now()
tempo = h.strftime("%d/%m/%Y %H:%M:%S")
hoje = h.strftime("%d/%m/%Y")
file_name = h.strftime("%d%m%y%H%M")
novoDirname = h.strftime("%m%Y")
mesDeAno = h.strftime("mês %m de %Y")

#criador de folder (diretório)
def novoDirCreate(nameDir = novoDirname):
    if not nameDir:
        print("É preciso dar um nome ao diretório!")
        return
    nameFolder = dirResultados + nameDir + '/'

    try:
        os.makedirs(nameFolder)
        return nameFolder
    except OSError as e:
        if e.errno == errno.EEXIST:
            print('Diretório já existe! Seguiremos com ele então...')
            return nameFolder
        else:
            raise

#TODO: setar headless True em produção
def set_driver_firefox(url, headless = False):


 # criando novo diretório onde ficarão armazenados os downloads
    dirDownloads = novoDirCreate()
    if not dirDownloads:
        print('Diretório para downloads não criado. Abortar...')
        return

    if os.path.isfile(dirDownloads + 'log.txt'):
        file = open(dirDownloads + 'log.txt', 'r')
        t = file.read()
        if 'email enviado' in t:
            print('Tarefa já cumprida para o ' + mesDeAno)
            return

    options = Options()
    #setando forefox como headless
    if(headless):
        options.headless = True
    
    #options = webdriver.FirefoxOptions()
    # setando forefox como headless
    # options.add_argument('-headless')

    profile = webdriver.FirefoxProfile()
    # para os downloads
    profile.set_preference("browser.download.dir", dirDownloads)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                           "application/pdf,application/octet-stream")
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.neverAsk.openFile",
                           "application/pdf,application/octet-stream")
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.manager.useWindow", False)
    profile.set_preference("browser.download.manager.focusWhenStarting", False)
    profile.set_preference("browser.download.manager.showAlertOnComplete", False)
    profile.set_preference("browser.download.manager.closeWhenDone", True)
    profile.set_preference("pdfjs.disabled", True)
    # para evitar chateação com certificado
    profile.accept_untrusted_certs = True

    # inicia o webdriver
    driver = webdriver.Firefox(firefox_profile=profile, options=options, service_log_path=os.devnull)
    driver.implicitly_wait(30)
    driver.set_page_load_timeout(240)

    # options = Options()
    # #setando forefox como headless
    # if(headless):
    #     options.headless = True
    # #inicia o webdriver com as options e sem gerar o geckodriver.log
    # driver = webdriver.Firefox(options=options, service_log_path=os.devnull)
    # driver.implicitly_wait(30)
    # driver.set_page_load_timeout(240)
    driver.get(url)
    return driver


#login no Esocial (e tudo mais...)
def esocial_action(bc = 'R$ 1.500,00'):

    driver = set_driver_firefox(lUrl)

    assert "eSocial" in driver.title
    cpf = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_txtNI"]')
    cod = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_txtCodigo"]')
    password = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_txtSenha"]')

    cpf.send_keys(lCpf)
    time.sleep(2)
    cod.send_keys(lCod)
    time.sleep(1)
    password.send_keys(lPass)
    time.sleep(2)

    enviar = driver.find_element_by_xpath('//*[@id="ContentPlaceHolder1_btnLogin"]')
    enviar.click()

    time.sleep(2)
    # clicar em continuar, dando 'enter'
    driver.find_element_by_css_selector("body").send_keys(Keys.ENTER)
    print('Loguei e dei um enter.')

    #acesso a folha de pagamentos
    folha = driver.find_elements_by_link_text('Folha de Pagamentos')
    if(folha):
        folha[1].click()
        time.sleep(2)


    # folha = WebDriverWait(driver, 100).until(
    #     EC.element_to_be_clickable((By.XPATH,'/html/body/div[3]/div[4]/div/div[2]/div[1]/ul/li[1]/a'))
    # )
    
    # clicar em continuar, dando 'enter'
    driver.find_element_by_css_selector("body").send_keys(Keys.ENTER)
    print('Cliquei em folha de pagamento e dei um novo enter.')

    encerrar_folha = WebDriverWait(driver, 100).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,'.encerrar-folha'))
    )

    if 'Folha Encerrada' in encerrar_folha.text:
        print('Folha do mês já estava encerrada...')
    else:

        # time.sleep(500)

        encerrar_folha.click()
        print('Cliquei em encerrar folha.')

        base_calculo = WebDriverWait(driver, 100).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,'table.table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(2)'))
        )

        #Confirmando a base de cálculo
        if bc == base_calculo.text:
            print(f'Confirmei a base de calculo: {bc}')
        else:
            print('Nao confirmei a base de calculo...' + base_calculo.text)
            return False

        btnConfirmar = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,'#btnConfirmar'))
        )

        #TODO !!!
        print('aqui seria a hora de encerrar a folha...')    
        driver.quit()
        return True

        btnConfirmar.click()
        print('Cliquei em confirmar fechamento da folha.')

    # #emitindo guia
    # btnGuia= WebDriverWait(driver, 100).until(
    #     EC.element_to_be_clickable((By.CSS_SELECTOR,'a.btn.pull-left'))
    # )

    btnGuia = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.XPATH,"//*[contains(text(), 'Emitir Guia')]"))
        )

    if btnGuia:
        btnGuia.click()
        print('Cliquei em emitir guia.')
    else:
        print('Problemas na emissão da guia...')
        return False

    time.sleep(2)

    btnRecibo = driver.find_element_by_css_selector("#InprimirRecibosPagamento")
    if btnRecibo:
        btnRecibo.click()
        print('Cliquei em emitir recibo.')
    else:
        print('Problemas na emissão do recibo...')

    return True


esocial_action()