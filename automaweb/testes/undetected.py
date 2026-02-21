import undetected_chromedriver as uc

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support.ui import WebDriverWait

from typing import Literal
import json
import os
from tkinter import messagebox
import tkinter as tk

class MeuBot:

    def __init__(self, tempo_stun: float = 0, navegador: Literal["edge", "chrome", "firefox" ] = "edge"):
        
        self.driver = None #driver do navegador
        self.wait = None #espera do driver
        self.stun = tempo_stun #tempo de stun entre as ações (em segundos)
        self.navegador = navegador.lower() #tipo do navegador (edge, chrome ou firefox)

    def abrir_driver_undetected(self, headless: bool = False, tempo_wait: int = 10):
        try:
            if self.navegador == "chrome":
                options = uc.ChromeOptions()
                
                # Configurações para o Chrome (Undetected)
                if headless:
                    # O UC precisa do argumento headless específico para não ser pego
                    options.add_argument('--headless')
                
                options.add_argument("--start-maximized")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-popup-blocking")

                # Inicializamos o Undetected Chromedriver
                self.driver = uc.Chrome(options=options)

            elif self.navegador == "firefox":
                #verificar código do Bento que usa Firefox
                pass

            else:
                messagebox.showwarning("Aviso", f"O navegador {self.navegador} ainda não tem suporte para o modo undetected.\nAbrindo o modo padrão...")
                self.abrir_driver()

            self.wait = WebDriverWait(self.driver, tempo_wait)
            print(f"Driver {self.navegador} iniciado com sucesso.")

        except Exception as e:
            print(f"Erro ao iniciar o driver: {e}")
            raise

    def abrir_url(self, url: str):

        '''
        Abre uma URL (precisa iniciar o driver primeiro).
        
        Args:
            url (str): A URL que deseja abrir no navegador.
        '''
        try:
            self.driver.get(url)
        except Exception as e:
            print(f"Erro ao abrir URL: {e}")
            raise

    def salvar_cookies(self, nome_arquivo: str = os.path.join(os.path.expanduser("~"), "Downloads", "cookies.json")):
        
        '''
        Coleta todos os cookies da sessão atual e salva em um arquivo JSON.
        É útil para manter o login em execuções futuras.

        Args:
            nome_arquivo (str): O nome do arquivo JSON onde os cookies serão salvos. Padrão é "cookies.json" na pasta Downloads.
        '''
  
        #exibe uma mensagem de aviso para o usuário
        #a ideia é que após clicar em ok, o código prossiga
        root = tk.Tk()
        root.attributes('-topmost', True) #deixa a janela sempre no topo
        root.withdraw()
        messagebox.showwarning(
            'Atenção',
            'Clique em "OK" apenas quando estiver pronto para salvar os cookies.',
            parent=root
        )
        root.destroy()

        try:
            #obtém lista de dicionários com os cookies
            cookies = self.driver.get_cookies()
            with open(nome_arquivo, 'w') as arquivo:
                json.dump(cookies, arquivo, indent=4)
        except Exception as e:
            print(f"Erro ao salvar cookies: {e}")
            raise
