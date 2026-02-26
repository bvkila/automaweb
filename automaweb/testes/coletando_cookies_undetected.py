import automaweb
import time

cookies = False

nav = automaweb.Navegador(navegador="chrome")

if cookies == False:
    nav.abrir_driver_undetected()
    nav.abrir_url('https://google.com')
    nav.salvar_cookies()
    nav.fechar_driver()

else:
    nav.abrir_driver()
    nav.abrir_url('https://google.com')
    nav.carregar_cookies()
    nav.recarregar_driver()
    nav.clicar('//*[text()="Portal do Parceiro"]')
    time.sleep(500)
