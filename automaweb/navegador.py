"""
Módulo com a classe Navegador para automação web.
"""

import logging
import platform
import time
import os
import json
import datetime
from functools import wraps
from typing import Literal

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium import webdriver
from tkinter import messagebox
import tkinter as tk
import undetected_chromedriver as uc
import requests
import yt_dlp

logger = logging.getLogger(__name__)


class Navegador:
    '''
    Classe principal para controle do navegador e interações com a página.

    Args:
        tempo_stun (float): Tempo de espera entre as ações (em segundos). Padrão é 0.
        navegador (str): Tipo do navegador (edge, chrome ou firefox). Padrão é "edge".
    '''

    def __init__(self, tempo_stun: float = 0, navegador: Literal["edge", "chrome", "firefox"] = "edge"):
        self.driver = None
        self.wait = None
        self.stun = tempo_stun
        self.navegador = navegador.lower()
        self._m3u8_capturadas: list[tuple[float, str]] = []

    def _aplicar_stun(self):
        '''Aguarda tempo_stun segundos entre ações.'''
        time.sleep(self.stun)

    @staticmethod
    def _corrigir_del_uc():
        '''Evita o OSError [WinError 6] quando o GC chama __del__ após quit() no uc.Chrome.'''
        if getattr(uc.Chrome, '_del_corrigido', False):
            return
        _del_original = uc.Chrome.__del__

        def _del_seguro(self):
            try:
                _del_original(self)
            except OSError:
                pass

        uc.Chrome.__del__ = _del_seguro
        uc.Chrome._del_corrigido = True

    @staticmethod
    def _encontrar_chrome() -> str | None:
        '''Procura o executável do Chrome nos caminhos padrão e no cache do Selenium.'''
        from undetected_chromedriver import find_chrome_executable
        caminho = find_chrome_executable()
        if caminho:
            return caminho
        cache = os.path.join(os.path.expanduser("~"), ".cache", "selenium", "chrome")
        if not os.path.isdir(cache):
            return None
        for plataforma in os.listdir(cache):
            dir_plataforma = os.path.join(cache, plataforma)
            if not os.path.isdir(dir_plataforma):
                continue
            for versao in sorted(os.listdir(dir_plataforma), reverse=True):
                for nome_bin in ("chrome.exe", "chrome"):
                    candidato = os.path.join(dir_plataforma, versao, nome_bin)
                    if os.path.isfile(candidato):
                        return candidato
        return None

    @staticmethod
    def _verifica_driver(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.driver is None or self.wait is None:
                logger.error(f"Tentativa de executar '{func.__name__}' sem driver. Use abrir_driver() primeiro.")
                return None
            return func(self, *args, **kwargs)
        return wrapper

    @staticmethod
    def _repetir_por_interceptacao(limite=3, delay=1):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                tentativas = 0
                excecoes_ignoradas = (
                    ElementClickInterceptedException,
                    ElementNotInteractableException,
                    StaleElementReferenceException,
                )
                while tentativas < limite:
                    try:
                        return func(*args, **kwargs)
                    except excecoes_ignoradas as e:
                        tentativas += 1
                        if tentativas == limite:
                            logger.warning(f"Limite de tentativas excedido ao executar '{func.__name__}': {e}")
                            raise
                        time.sleep(delay)
                    except Exception as e:
                        logger.error(f"Erro ao executar '{func.__name__}': {e}")
                        raise
                return None
            return wrapper
        return decorator

    # --- INICIALIZAÇÃO DO DRIVER ---

    def abrir_driver(self, headless: bool = False, tempo_wait: int = 10):
        '''
        Inicializa o driver baseado na escolha feita no __init__ (Edge, Chrome ou Firefox).

        Args:
            headless (bool): Se True, o navegador será iniciado em modo headless. Padrão é False.
            tempo_wait (int): Tempo de espera do driver (em segundos). Padrão é 10.
        '''
        try:
            if self.navegador in ("chrome", "edge"):
                options = ChromeOptions() if self.navegador == "chrome" else EdgeOptions()
                options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument("--log-level=3")
                options.add_argument("--start-maximized")
                if headless:
                    options.add_argument("--headless=new")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                self.driver = webdriver.Chrome(options=options) if self.navegador == "chrome" else webdriver.Edge(options=options)

            elif self.navegador == "firefox":
                options = FirefoxOptions()
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference("useAutomationExtension", False)
                options.log.level = "fatal"
                if headless:
                    options.add_argument("-headless")
                self.driver = webdriver.Firefox(options=options)

            else:
                raise ValueError(f"Navegador '{self.navegador}' não suportado. Escolha entre: edge, chrome, firefox.")

            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, tempo_wait)

        except Exception as e:
            logger.error(f"Erro ao iniciar o driver ({self.navegador}): {e}")
            raise

    def abrir_driver_undetected(self, headless: bool = False, tempo_wait: int = 10, caminho_driver: str = None, caminho_edge_linux: str = '/usr/bin/microsoft-edge'):
        '''
        Inicializa o WebDriver em modo oculto (Undetected) para evitar detecção anti-bot.

        Args:
            headless (bool): Se True, inicia sem interface gráfica. Padrão é False.
            tempo_wait (int): Tempo de espera implícito em segundos. Padrão é 10.
            caminho_driver (str, optional): Caminho para o executável do WebDriver. Padrão é None.
            caminho_edge_linux (str): Caminho do Edge em Linux. Padrão é '/usr/bin/microsoft-edge'.
        '''
        try:
            if self.navegador == "chrome":
                options = uc.ChromeOptions()
                if headless:
                    options.add_argument('--headless')
                    options.add_argument("--disable-popup-blocking")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-extensions")
                chrome_path = self._encontrar_chrome()
                self.driver = uc.Chrome(options=options, browser_executable_path=chrome_path)

            elif self.navegador == "edge":
                options = EdgeOptions()
                options.use_chromium = True
                sistema = platform.system()
                if sistema == "Windows":
                    options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                elif sistema == "Linux":
                    options.binary_location = caminho_edge_linux
                if headless:
                    options.headless()
                    options.add_argument("--disable-popup-blocking")
                options.add_argument("--start-maximized")
                options.add_argument("--disable-sync")
                options.add_argument("--disable-extensions")
                options.add_argument("--no-default-browser-check")
                options.add_argument("--no-first-run")
                options.add_argument("--disable-notifications")
                options.add_argument("--disable-features=msEdgeFirstRunExperience,msFre")
                options.add_experimental_option("prefs", {"profile.default_content_settings.popups": 1})
                self.driver = uc.Chrome(options=options, driver_executable_path=caminho_driver)

            if self.navegador in ("chrome", "edge"):
                self._corrigir_del_uc()
                self.driver.maximize_window()
                self.wait = WebDriverWait(self.driver, tempo_wait)
            else:
                logger.warning(f"O navegador {self.navegador} ainda não tem suporte para o modo undetected. Abrindo o modo padrão...")
                self.abrir_driver()

        except Exception as e:
            logger.error(f"Erro ao iniciar o driver undetected: {e}")
            raise

    # --- NAVEGAÇÃO ---

    @_verifica_driver
    def abrir_url(self, url: str):
        '''
        Abre uma URL no navegador.

        Args:
            url (str): A URL que deseja abrir.
        '''
        try:
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Erro ao abrir URL: {e}")
            raise

    @_verifica_driver
    def abrir_nova_aba(self, url: str):
        '''
        Abre uma nova aba e foca nela automaticamente.

        Args:
            url (str): A URL que deseja abrir na nova aba.
        '''
        try:
            self.driver.switch_to.new_window('tab')
            self.driver.get(url)
        except Exception as e:
            logger.error(f"Erro ao abrir nova aba: {e}")
            raise

    @_verifica_driver
    def alternar_aba(self, indice: int):
        '''
        Muda o foco para a aba pelo índice (0 é a primeira).

        Args:
            indice (int): O índice da aba.
        '''
        try:
            abas = self.driver.window_handles
            self.driver.switch_to.window(abas[indice])
        except Exception as e:
            logger.error(f"Erro ao mudar para a aba {indice}: {e}")
            raise

    @_verifica_driver
    def fechar_aba(self):
        '''Fecha a aba atual e retorna o foco para a última aba aberta.'''
        try:
            self.driver.close()
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[-1])
        except Exception as e:
            logger.error(f"Erro ao fechar aba: {e}")
            raise

    @_verifica_driver
    def recarregar_driver(self):
        '''Recarrega a página atual.'''
        try:
            self.driver.refresh()
        except Exception as e:
            logger.error(f"Erro ao recarregar a página: {e}")
            raise

    @_verifica_driver
    def fechar_driver(self):
        '''Fecha o navegador e encerra a sessão do driver.'''
        try:
            self.driver.quit()
        except Exception as e:
            logger.error(f"Erro ao fechar o driver: {e}")
            raise

    # --- INTERAÇÕES COM A PÁGINA ---

    @_repetir_por_interceptacao()
    def clicar(self, xpath: str):
        '''
        Clica em um elemento identificado pelo xpath.

        Args:
            xpath (str): O XPath do elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elemento.click()
        except:
            raise

    @_verifica_driver
    def clicar_script(self, xpath: str):
        '''
        Clica em um elemento via JavaScript.
        Útil quando o clique padrão é bloqueado por sobreposições.

        Args:
            xpath (str): O XPath do elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.driver.find_element(By.XPATH, xpath)
            self.driver.execute_script("arguments[0].click();", elemento)
        except Exception as e:
            logger.error(f"Erro ao clicar via script: {e}")
            raise

    def clicar_forcado(self, xpath: str):
        '''
        Clica em um elemento sem verificar se é clicável.
        Útil para campos ocultos ou sobrepostos.

        Args:
            xpath (str): O XPath do elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            elemento.click()
        except:
            raise

    @_repetir_por_interceptacao()
    def digitar(self, xpath: str, texto: str):
        '''
        Digita um texto em um elemento.

        Args:
            xpath (str): O XPath do elemento.
            texto (str): O texto a digitar.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elemento.send_keys(texto)
        except:
            raise

    def digitar_forcado(self, xpath: str, texto: str):
        '''
        Digita sem verificar se o campo é clicável.

        Args:
            xpath (str): O XPath do elemento.
            texto (str): O texto a digitar.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            elemento.send_keys(texto)
        except:
            raise

    @_repetir_por_interceptacao()
    def limpar(self, xpath: str):
        '''
        Limpa o conteúdo de um campo de entrada.

        Args:
            xpath (str): O XPath do elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            elemento.clear()
        except:
            raise

    @_repetir_por_interceptacao()
    def passar_mouse(self, xpath: str):
        '''
        Simula o hover do mouse sobre um elemento.

        Args:
            xpath (str): O XPath do elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            ActionChains(self.driver).move_to_element(elemento).perform()
        except:
            raise

    @_repetir_por_interceptacao()
    def selecionar_texto(self, xpath: str, texto: str):
        '''
        Seleciona uma opção pelo texto visível em um elemento select.

        Args:
            xpath (str): O XPath do elemento select.
            texto (str): O texto da opção a selecionar.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            Select(elemento).select_by_visible_text(texto)
        except:
            raise

    @_repetir_por_interceptacao()
    def selecionar_valor(self, xpath: str, valor: int):
        '''
        Seleciona uma opção pelo valor em um elemento select.

        Args:
            xpath (str): O XPath do elemento select.
            valor (int): O valor da opção a selecionar.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            Select(elemento).select_by_value(valor)
        except:
            raise

    @_repetir_por_interceptacao()
    def obter_texto(self, xpath: str) -> str:
        '''
        Obtém o texto de um elemento.

        Args:
            xpath (str): O XPath do elemento.

        Returns:
            str: O texto do elemento.
        '''
        try:
            elemento = self.wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
            return elemento.text
        except:
            raise

    @_verifica_driver
    def obter_texto_script(self, xpath: str) -> str:
        '''
        Obtém o texto de um elemento via JavaScript.
        Útil quando .text retorna vazio em elementos com conteúdo dinâmico.

        Args:
            xpath (str): O XPath do elemento.

        Returns:
            str: O textContent do elemento.
        '''
        try:
            elemento = self.driver.find_element(By.XPATH, xpath)
            return self.driver.execute_script("return arguments[0].textContent;", elemento)
        except Exception as e:
            logger.error(f"Erro ao obter texto via script: {e}")
            raise

    @_repetir_por_interceptacao()
    def obter_atributo(self, xpath: str, atributo: str) -> str:
        '''
        Obtém o valor de um atributo de um elemento.

        Args:
            xpath (str): O XPath do elemento.
            atributo (str): O nome do atributo (ex: 'value', 'href', 'src').

        Returns:
            str: O valor do atributo.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return elemento.get_attribute(atributo)
        except:
            raise

    @_repetir_por_interceptacao()
    def rolar_ate_elemento(self, xpath: str):
        '''
        Rola a tela até o elemento ficar visível.

        Args:
            xpath (str): O XPath do elemento.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
        except:
            raise

    @_repetir_por_interceptacao()
    def aguardar_elemento_sumir(self, xpath: str):
        '''
        Aguarda até o elemento não estar mais visível.

        Args:
            xpath (str): O XPath do elemento.
        '''
        try:
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, xpath)))
        except:
            raise

    @_repetir_por_interceptacao()
    def encontrar_elemento(self, xpath: str):
        '''
        Retorna o primeiro elemento encontrado pelo xpath.

        Args:
            xpath (str): O XPath do elemento.

        Returns:
            WebElement: O primeiro elemento encontrado.
        '''
        try:
            self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return self.driver.find_element(By.XPATH, xpath)
        except:
            raise

    @_repetir_por_interceptacao()
    def encontrar_elementos(self, xpath: str):
        '''
        Retorna todos os elementos encontrados pelo xpath.

        Args:
            xpath (str): O XPath dos elementos.

        Returns:
            list: Lista de WebElements encontrados.
        '''
        try:
            return self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
        except:
            raise

    @_verifica_driver
    def tirar_screenshot(self, nome_arquivo: str = None):
        '''
        Salva uma captura da tela atual na pasta Downloads.

        Args:
            nome_arquivo (str): Nome do arquivo sem extensão. Padrão é "screenshot_YYYYMMDD_HHMMSS".
        '''
        if nome_arquivo is None:
            nome_arquivo = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S")
        try:
            self.driver.save_screenshot(os.path.join(os.path.expanduser("~"), "Downloads", f"{nome_arquivo}.png"))
        except Exception as e:
            logger.error(f"Erro ao tirar screenshot: {e}")
            raise

    # --- IFRAME ---

    @_verifica_driver
    def entrar_iframe(self, xpath: str):
        '''
        Muda o foco do driver para dentro de um iframe.

        Args:
            xpath (str): O XPath do iframe.
        '''
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))
        except Exception as e:
            logger.error(f"Erro ao entrar no iframe: {e}")
            raise

    @_verifica_driver
    def sair_iframe(self):
        '''Retorna o foco para a página principal (saindo de qualquer iframe).'''
        try:
            self.driver.switch_to.default_content()
        except Exception as e:
            logger.error(f"Erro ao sair do iframe: {e}")
            raise

    # --- COOKIES ---

    @_verifica_driver
    def salvar_cookies(self, nome_arquivo: str = None):
        '''
        Salva os cookies da sessão atual em um arquivo JSON.

        Args:
            nome_arquivo (str): Caminho do arquivo JSON. Padrão é "cookies.json" na pasta Downloads.
        '''
        if nome_arquivo is None:
            nome_arquivo = os.path.join(os.path.expanduser("~"), "Downloads", "cookies.json")

        root = tk.Tk()
        root.attributes('-topmost', True)
        root.withdraw()
        messagebox.showwarning(
            'Atenção',
            'Clique em "OK" apenas quando estiver pronto para salvar os cookies.',
            parent=root
        )
        root.destroy()

        try:
            cookies = self.driver.get_cookies()
            with open(nome_arquivo, 'w') as arquivo:
                json.dump(cookies, arquivo, indent=4)
        except Exception as e:
            logger.error(f"Erro ao salvar cookies: {e}")
            raise

    @_verifica_driver
    def carregar_cookies(self, nome_arquivo: str = None):
        '''
        Carrega cookies de um arquivo JSON e recarrega a página.
        A URL precisa estar carregada antes de chamar este método.

        Args:
            nome_arquivo (str): Caminho do arquivo JSON. Padrão é "cookies.json" na pasta Downloads.
        '''
        if nome_arquivo is None:
            nome_arquivo = os.path.join(os.path.expanduser("~"), "Downloads", "cookies.json")

        try:
            with open(nome_arquivo, 'r') as arquivo:
                cookies = json.load(arquivo)
            for cookie in cookies:
                try:
                    if 'domain' in cookie:
                        del cookie['domain']
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    if 'sameSite' in cookie:
                        del cookie['sameSite']
                    self.driver.add_cookie(cookie)
                except Exception as e_cookie:
                    logger.warning(f"Ignorando cookie '{cookie.get('name', 'desconhecido')}': {e_cookie}")
            self.recarregar_driver()

        except FileNotFoundError:
            logger.warning(f"Arquivo '{nome_arquivo}' não existe. Faça o login manual primeiro.")

        except Exception as e:
            logger.error(f"Erro ao carregar cookies: {e}")
            raise

    # --- MÍDIA ---

    @_verifica_driver
    def baixar_video(self, url_mestre: str, nome_arquivo: str):
        '''
        Baixa um vídeo usando yt-dlp.

        Args:
            url_mestre (str): A URL do vídeo ou playlist .m3u8.
            nome_arquivo (str): O caminho de destino do arquivo (sem extensão).
        '''
        logger.info("Iniciando download com yt-dlp...")
        ydl_opts = {
            'referer': 'https://cursinhosimples.learnworlds.com/',
            'outtmpl': f'{nome_arquivo}.mp4',
            'continuedl': True,
            'limit_rate': '3M',
            'quiet': False,
            'nocheckcertificate': True,
            'windowsfilenames': True,
            'nopart': True,
            'overwrites': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_mestre])
        logger.info("Download concluido com sucesso.")

    @_verifica_driver
    def capturar_url_m3u8(self) -> list[str]:
        '''
        Lê URLs .m3u8 do Performance API no contexto atual (página ou iframe focado)
        e armazena em _m3u8_capturadas para uso por capturar_com_selenium().

        Returns:
            list[str]: Lista de URLs .m3u8 encontradas.
        '''
        urls = self.driver.execute_script(
            "return performance.getEntriesByType('resource')"
            ".map(function(e){return e.name;})"
            ".filter(function(n){return n.indexOf('.m3u8')!==-1 && !n.endsWith('.ts');});"
        ) or []
        for url in urls:
            self._m3u8_capturadas.append((time.time(), url))
            logger.info(f"[m3u8] Capturada: {url}")
        return urls

    @_verifica_driver
    def capturar_com_selenium(self, nome_arquivo: str):
        '''
        Baixa o vídeo cuja URL .m3u8 foi capturada por capturar_url_m3u8().
        Chame capturar_url_m3u8() dentro do iframe do vídeo antes de chamar este método.

        Args:
            nome_arquivo (str): O caminho de destino do arquivo (sem extensão).
        '''
        diretorio = os.path.dirname(nome_arquivo)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)

        link_capturado = None
        janela = time.time() - 30

        for _ in range(30):
            candidatas = [url for ts, url in self._m3u8_capturadas if ts >= janela]
            if candidatas:
                link_capturado = candidatas[0]
                self._m3u8_capturadas = [(ts, u) for ts, u in self._m3u8_capturadas if u != link_capturado]
                break
            time.sleep(1)

        if link_capturado:
            logger.info(f"[m3u8] Baixando: {link_capturado}")
            self.baixar_video(link_capturado, nome_arquivo)
        else:
            logger.warning("[m3u8] Nenhuma URL encontrada. Chame capturar_url_m3u8() dentro do iframe antes.")

    @_verifica_driver
    def baixar_imagem(self, xpath: str, nome: str):
        '''
        Baixa uma imagem a partir do atributo src de um elemento.

        Args:
            xpath (str): O XPath do elemento img.
            nome (str): O caminho de destino do arquivo (sem extensão).
        '''
        elemento = self.encontrar_elemento(xpath)
        url_imagem = elemento.get_attribute("src")
        resposta = requests.get(url_imagem)

        diretorio = os.path.dirname(nome)
        if diretorio:
            os.makedirs(diretorio, exist_ok=True)

        if resposta.status_code == 200:
            with open(f"{nome}.png", "wb") as png:
                png.write(resposta.content)
            logger.info(f"Imagem salva: {nome}.png")
        else:
            logger.error(f"Falha ao baixar imagem. Codigo: {resposta.status_code}")

    # --- VERIFICAÇÕES ---

    @_verifica_driver
    def verifica_selecionado(self, xpath: str) -> bool:
        '''
        Verifica se um elemento está selecionado.

        Args:
            xpath (str): O XPath do elemento.

        Returns:
            bool: True se selecionado, False caso contrário.
        '''
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return elemento.is_selected()
        except Exception as e:
            logger.error(f"Erro ao verificar se o elemento esta selecionado: {e}")
            raise

    @_verifica_driver
    def verifica_habilitado(self, xpath: str) -> bool:
        '''
        Verifica se um elemento está habilitado.

        Args:
            xpath (str): O XPath do elemento.

        Returns:
            bool: True se habilitado, False caso contrário.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return elemento.is_enabled()
        except Exception as e:
            logger.error(f"Erro ao verificar se o elemento esta habilitado: {e}")
            raise

    @_verifica_driver
    def verifica_clicavel(self, xpath: str, timeout: float = 10) -> bool:
        '''
        Verifica se um elemento é clicável.

        Args:
            xpath (str): O XPath do elemento.
            timeout (float): Tempo máximo de espera em segundos. Padrão é 10.

        Returns:
            bool: True se clicável, False caso contrário.
        '''
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return True
        except Exception:
            return False

    @_verifica_driver
    def verifica_existe(self, xpath: str, timeout: float = 10) -> bool:
        '''
        Verifica se um elemento existe na página.

        Args:
            xpath (str): O XPath do elemento.
            timeout (float): Tempo máximo de espera em segundos. Padrão é 10.

        Returns:
            bool: True se existir, False caso contrário.
        '''
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except Exception:
            return False

    @_verifica_driver
    def verifica_visivel(self, xpath: str, timeout: float = 10) -> bool:
        '''
        Verifica se um elemento está visível na página.

        Args:
            xpath (str): O XPath do elemento.
            timeout (float): Tempo máximo de espera em segundos. Padrão é 10.

        Returns:
            bool: True se visível, False caso contrário.
        '''
        try:
            elemento = WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return elemento.is_displayed()
        except Exception:
            return False

    @_verifica_driver
    def verificar_texto_digitado(self, xpath: str, texto_esperado: str) -> bool:
        '''
        Verifica se o valor de um campo é igual ao texto esperado.

        Args:
            xpath (str): O XPath do campo.
            texto_esperado (str): O texto esperado.

        Returns:
            bool: True se igual, False caso contrário.
        '''
        try:
            valor_atual = self.obter_atributo(xpath, 'value')
            return valor_atual == texto_esperado
        except Exception as e:
            logger.error(f"Erro ao verificar o texto digitado: {e}")
            raise

    @_verifica_driver
    def verificar_texto_selecionado(self, xpath: str, texto_esperado: str) -> bool:
        '''
        Verifica se a opção selecionada em um select é igual ao texto esperado.

        Args:
            xpath (str): O XPath do select.
            texto_esperado (str): O texto esperado.

        Returns:
            bool: True se igual, False caso contrário.
        '''
        try:
            texto_atual = self.obter_texto_selecionado(xpath)
            return texto_atual == texto_esperado
        except Exception as e:
            logger.error(f"Erro ao verificar o select: {e}")
            raise

    @_verifica_driver
    def obter_texto_selecionado(self, xpath: str) -> str:
        '''
        Obtém o texto da opção selecionada em um elemento select.

        Args:
            xpath (str): O XPath do select.

        Returns:
            str: O texto da opção selecionada.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return Select(elemento).first_selected_option.text
        except Exception as e:
            logger.error(f"Erro ao obter o texto selecionado: {e}")
            raise