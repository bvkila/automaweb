import automaweb
import time
from credenciais_teste import *

cookies = True

nav = automaweb.Navegador(navegador="chrome")

if cookies == False:
    nav.abrir_driver_undetected()
    nav.abrir_url(site_teste)
    nav.salvar_cookies(caminho_teste)
    nav.fechar_driver()

else:
    nav.abrir_driver()
    nav.abrir_url(site_teste)
    nav.carregar_cookies(caminho_teste)
    nav.recarregar_driver()
    nav.clicar('//*[text()="Portal do Parceiro"]')
    time.sleep(500)
