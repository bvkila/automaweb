"""
biblioteca destinada à automatização de tarefas na web
bem como interações com o gerenciamento de arquivos no computador
"""

#bibliotecas do Selenium para controle do navegador e interações com a página
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium import webdriver

#biblioteca para criar decoradores e 
from functools import wraps
from typing import Literal

#biblioteca para interface gráfica
from tkinter import messagebox
from tkinter import filedialog
import tkinter as tk

#bibliotecas para manipulação de arquivos e pastas
import datetime
import shutil
import time
import json
import os

class Navegador:
    '''
    Classe principal para controle do navegador e interações com a página.
    
    Args:
        tempo_stun (float): Tempo de espera entre as ações (em segundos). Padrão é 0.
        navegador (str): O tipo do navegador a ser controlado ("edge", "chrome" ou "firefox"). Padrão é "edge".
    '''
    def __init__(self, tempo_stun: float = 0, navegador: Literal["edge", "chrome", "firefox" ] = "edge"):
        
        self.driver = None #driver do navegador
        self.wait = None #espera do driver
        self.stun = tempo_stun #tempo de stun entre as ações (em segundos)
        self.navegador = navegador.lower() #tipo do navegador (edge, chrome ou firefox)

    def _aplicar_stun(self):

        '''função interna que espera tempo_stun segundos'''
        time.sleep(self.stun)

    @staticmethod
    def _verifica_driver(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            
            #criando um decorador para verificar se o driver foi inicializado antes de executar a função decorada.
            if self.driver is None or self.wait is None:
                messagebox.showerror(
                    "Erro Crítico", 
                    f"Tentativa de executar '{func.__name__}' sem driver.\nUse abrir_driver() primeiro."
                )
                return None  #cancela a ação original aqui
            
            #se passou no if acima, executamos a função original passando os argumentos
            return func(self, *args, **kwargs)
        
        #o decorador devolve o wrapper para substituir a função original
        return wrapper
 
    @staticmethod
    def _repetir_por_interceptacao(limite=3, delay=1):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                tentativas = 0
                #lista de exceções de "impedimento"
                excecoes_ignordas = (
                    ElementClickInterceptedException, 
                    ElementNotInteractableException,
                    StaleElementReferenceException
                ) #sempre que uma dessas exceções ocorrer, ele tenta novamente
                
                while tentativas < limite:
                    try:
                        return func(*args, **kwargs)
                    except excecoes_ignordas as e:
                        tentativas += 1
                        if tentativas == limite:
                            raise e
                        time.sleep(delay)
                return None
            return wrapper
        return decorator

### NAVEGAÇÕES DENTRO DO DRIVER


    def abrir_driver(self, headless: bool = False):
        '''
        Inicializa o driver baseado na escolha feita no __init__ (Edge, Chrome ou Firefox).

        Args:
            headless (bool): Se True, o navegador será iniciado em modo headless. Padrão é False.
        '''
        try:
            if self.navegador == "chrome":
                
                options = ChromeOptions()
                #configurações anti-detecção e log
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument("--log-level=3")
                options.add_argument("--start-maximized")
                if headless:
                    options.add_argument("--headless=new")
                self.driver = webdriver.Chrome(options=options)

            elif self.navegador == "firefox":
                
                options = FirefoxOptions()
                #configurações anti-detecção e log
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference("useAutomationExtension", False)
                options.log.level = "fatal" #reduz o nível de log do Geckodriver para evitar poluição no terminal                
                if headless:
                    options.add_argument("-headless")
                self.driver = webdriver.Firefox(options=options)

            elif self.navegador == "edge":
                
                options = EdgeOptions()
                #configurações anti-detecção e log
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument("--log-level=3")
                options.add_argument("--start-maximized")
                if headless:
                    options.add_argument("--headless=new")
                self.driver = webdriver.Edge(options=options)
            
            else:
                raise ValueError(f"Navegador '{self.navegador}' não suportado. Escolha entre: edge, chrome, firefox.")

            #configurações globais após iniciar o driver
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 10)

        except Exception as e:
            print(f"Erro ao iniciar o driver ({self.navegador}): {e}")
            raise

    @_verifica_driver
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
    
    @_verifica_driver
    def abrir_nova_aba(self, url: str):

        '''
        Abre uma nova aba e foca nela automaticamente.
        
        Args:
            url (str): A URL que deseja abrir na nova aba.
        '''
        try:
            # 'tab' abre uma aba. 'window' abriria uma nova janela separada.
            self.driver.switch_to.new_window('tab') 
            self.driver.get(url)
        except Exception as e:
            print(f"Erro ao abrir nova aba: {e}")
            raise
    
    @_verifica_driver
    def alternar_aba(self, indice: int):

        '''
        Muda o foco para a aba especificada pelo índice (0 é a primeira, 1 é a segunda...).
        
        Args:
            indice (int): O índice da aba para a qual deseja alternar.
        '''
        try:
            abas = self.driver.window_handles
            self.driver.switch_to.window(abas[indice])
        except Exception as e:
            print(f"Erro ao mudar para a aba {indice}: {e}")
            raise

    @_verifica_driver  
    def fechar_aba(self):
    
        '''
        Fecha a aba atual e volta o foco para a aba anterior (se houver).
        '''  
        try:
            # .close() fecha SÓ a aba atual (diferente de .quit() que fecha tudo)
            self.driver.close()
            
            #boa prática: voltar o foco para a última aba aberta para não ficar "sem foco"
            if len(self.driver.window_handles) > 0:
                self.driver.switch_to.window(self.driver.window_handles[-1])
        except Exception as e:
            print(f"Erro ao fechar aba: {e}")
            raise

    @_verifica_driver
    def recarregar_driver(self):
        
        '''
        Recarrega (atualiza) a página atual (F5).
        '''
        try:
            self.driver.refresh()
        except Exception as e:
            print(f"Erro ao recarregar a página: {e}")
            raise

    @_verifica_driver
    def fechar_driver(self):

        '''
        Fecha o navegador e encerra a sessão do driver.
        ''' 
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Erro ao fechar o driver: {e}")
            raise

### INTERAÇÕES COM A PÁGINA

    @_repetir_por_interceptacao()
    def clicar(self, xpath: str):
    
        '''
        Clica em um elemento identificado pelo xpath.
        
        Args:
            xpath (str): O XPath do elemento que deseja clicar.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))) #aguardar ser clicável
            elemento.click()
        except Exception as e:
            print(f"Erro ao clicar no elemento: {e}")
            raise

    @_repetir_por_interceptacao()
    def digitar(self, xpath: str, texto: str):
        
        '''
        Digita um texto em um elemento identificado pelo xpath.
        
        Args:
            xpath (str): O XPath do elemento que deseja digitar.
            texto (str): O texto que deseja digitar no elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))) #aguardar ser clicável
            elemento.send_keys(texto)
        except Exception as e:
            print(f"Erro ao digitar no elemento: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def limpar(self, xpath: str):

        '''
        Limpa o conteúdo de um elemento de entrada.
        
        Args:
            xpath (str): O XPath do elemento que deseja limpar.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))) #aguardar ser clicável
            elemento.clear()
        except Exception as e:
            print(f"Erro ao limpar o elemento: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def passar_mouse(self, xpath: str):
        
        '''
        Simula a ação de mover o cursor do mouse sobre o elemento (Hover).
        
        Args:
            xpath (str): O XPath do elemento sobre o qual deseja passar o mouse.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath))) #aguardar ser clicável
            actions = ActionChains(self.driver)
            actions.move_to_element(elemento).perform()
        except Exception as e:
            print(f"Erro ao passar o mouse sobre o elemento: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def selecionar_texto(self, xpath: str, texto: str):

        '''
        Seleciona um texto dentro de um elemento.
        
        Args:
            xpath (str): O XPath do elemento que deseja selecionar o texto.
            texto (str): O texto que deseja selecionar dentro do elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))

            Select(elemento).select_by_visible_text(texto)
        except Exception as e:
            print(f"Erro ao selecionar o texto {texto}: {e}")
            raise

    @_repetir_por_interceptacao()
    def selecionar_valor(self, xpath: str, valor: int):

        '''
        Seleciona um valor dentro de um elemento.
        
        Args:
            xpath (str): O XPath do elemento que deseja selecionar o valor.
            valor (int): O valor que deseja selecionar dentro do elemento.
        '''
        self._aplicar_stun()
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            Select(elemento).select_by_value(valor)
        except Exception as e:
            print(f"Erro ao selecionar o valor {valor}: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def obter_texto(self, xpath: str):

        '''
        Obtém o texto de um elemento.
        
        Args:
            xpath (str): O XPath do elemento do qual deseja obter o texto.

        Returns:
            str: O texto do elemento.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return elemento.text
        except Exception as e:
            print(f"Erro ao obter o texto do elemento: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def obter_atributo(self, xpath: str, atributo: str):

        '''
        Obtém o atributo de um elemento.
        
        Args:
            xpath (str): O XPath do elemento do qual deseja obter o atributo.
            atributo (str): O nome do atributo que deseja obter. Ex: 'value' para campos de entrada, 'href' para links, etc.

        Returns:
            str: O valor do atributo do elemento.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return elemento.get_attribute(atributo)
        except Exception as e:
            print(f"Erro ao obter o atributo do elemento: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def rolar_ate_elemento(self, xpath: str):
        
        '''
        Rola a tela até que o elemento específico esteja visível.
        
        Args:
            xpath (str): O XPath do elemento até o qual deseja rolar a tela.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", elemento)
        except Exception as e:
            print(f"Erro ao rolar a tela até o elemento: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def aguardar_elemento_sumir(self, xpath: str):
        
        '''
        Aguarda até que o elemento não esteja mais visível.
        
        Args:
            xpath (str): O XPath do elemento que deseja aguardar sumir.
        '''
        try:
            self.wait.until(EC.invisibility_of_element_located((By.XPATH, xpath)))
        except Exception as e:
            print(f"Erro ao aguardar o elemento sumir: {e}")
            raise
    
    @_repetir_por_interceptacao()
    def encontrar_elementos(self, xpath: str):
        
        '''
        Retorna uma lista com todos os elementos identificados pelo xpath.
        
        Args:
            xpath (str): O XPath dos elementos que deseja encontrar.
            
        Returns:
            list: Uma lista com todos os elementos encontrados.
        '''
        try:
            return self.driver.find_elements(By.XPATH, xpath)
        except Exception as e:
            print(f"Erro ao encontrar elementos: {e}")
            raise

    def tirar_screenshot(self, nome_arquivo: str = datetime.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S")):
        
        '''
        Salva uma imagem da tela atual na pasta Downloads.
        
        Args:
            nome_arquivo (str): O nome do arquivo para salvar a screenshot (sem extensão). Padrão é "screenshot_YYYYMMDD_HHMMSS" para evitar sobrescritas.
        '''

        try:
            self.driver.save_screenshot(f"{os.getlogin()}/Downloads/{nome_arquivo}.png")
        except Exception as e:
            print(f"Erro ao tirar screenshot: {e}")
            raise
    
    def entrar_iframe(self, xpath: str):
        
        '''
        Muda o foco do driver para dentro de um iframe.
        
        Args:
            xpath (str): O XPath do iframe que deseja entrar.
        '''
        try:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, xpath)))
        except Exception as e:
            print(f"Erro ao entrar no iframe: {e}")
            raise

    def sair_iframe(self):
        
        '''
        Volta o foco para a página principal.
        
        Args:
            xpath (str): O XPath do iframe que deseja entrar.
        '''
        try:
            self.driver.switch_to.default_content()
        except Exception as e:
            print(f"Erro ao sair do iframe: {e}")
            raise
    
    def salvar_cookies(self, nome_arquivo: str = f"{os.getlogin()}/Downloads/cookies.json"):
        
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
    
    def carregar_cookies(self, nome_arquivo: str = f"{os.getlogin()}/Downloads/cookies.json"):

        '''
        Carrega os cookies salvos em um arquivo JSON.

        Args:
            nome_arquivo (str): O nome do arquivo JSON de onde os cookies serão carregados. Padrão é "cookies.json" na pasta Downloads.
        '''

        #a URL precisa já estar carregada para o carregamento funcionar.'''
        try:
            with open(nome_arquivo, 'r') as arquivo:
                cookies = json.load(arquivo)
            for cookie in cookies:
                try:
                    #remove o domínio para evitar erro de "Invalid Cookie Domain".
                    #o selenium vai atribuir o cookie ao domínio atual automaticamente.
                    if 'domain' in cookie:
                        del cookie['domain']

                    #garante que a expiração seja um número inteiro (alguns salvam como float)
                    if 'expiry' in cookie:
                        cookie['expiry'] = int(cookie['expiry'])
                    
                    #remove sameSite se existir, pois causa conflitos frequentes em Chrome/Edge
                    if 'sameSite' in cookie:
                        del cookie['sameSite']

                    #adiciona o cookie limpo
                    self.driver.add_cookie(cookie)
                
                except Exception as e_cookie:
                    #é normal alguns cookies falharem (ex: cookies de sessão já expirados)
                    print(f"Ignorando cookie '{cookie.get('name', 'desconhecido')}': {e_cookie}")
            self.recarregar_driver() 

        except FileNotFoundError:
            messagebox.showwarning("Aviso", f"Arquivo '{nome_arquivo}' não existe. Faça o login manual primeiro.")

        except Exception as e:
            print(f"Erro ao carregar cookies: {e}")
            raise

### VERIFICAÇÕES


    def verifica_selecionado(self, xpath: str):
        '''
        Verifica se um elemento está selecionado (Retorna True ou False).
        
        Args:
            xpath (str): O XPath do elemento que deseja verificar.

        Returns:
            bool: True se o elemento estiver selecionado, False caso contrário.
        '''
        try:
            elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return elemento.is_selected()
        except Exception as e:
            print(f"Erro ao verificar se o elemento está selecionado: {e}")
            raise

    def verifica_habilitado(self, xpath: str):
        '''
        Verifica se um elemento está habilitado (Retorna True ou False).
        
        Args:
            xpath (str): O XPath do elemento que deseja verificar.

        Returns:
            bool: True se o elemento estiver habilitado, False caso contrário.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            return elemento.is_enabled()
        except Exception as e:
            print(f"Erro ao verificar se o elemento está habilitado: {e}")
            raise

    def verifica_clicavel(self, xpath: str, timeout: float):
        '''
        Verifica se um elemento é clicavel (Retorna True ou False).
        
        Args:
            xpath (str): O XPath do elemento que deseja verificar.
            timeout (float): Tempo máximo de espera para o elemento ser clicável.

        Returns:
            bool: True se o elemento é clicavel, False caso contrário.
        '''
        try:
            WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            return True
        except Exception as e:
            print(f"Elemento não é clicável após {timeout} segundos: {xpath}.\n Erro: {e}")
            return False

    def verifica_existe(self, xpath: str, timeout: float):
        '''
        Verifica se um elemento existe na página (Retorna True ou False).
        
        Args:
            xpath (str): O XPath do elemento que deseja verificar.
            timeout (float): Tempo máximo de espera para o elemento existir.

        Returns:
            bool: True se o elemento existir, False caso contrário.
        '''
        try:
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((By.XPATH, xpath)))
            return True
        except Exception as e:
            print(f"Elemento não existe após {timeout} segundos: {xpath}.\n Erro: {e}")
            return False
    
    def verificar_texto_digitado(self, xpath: str, texto_esperado: str ):
        '''
        Verifica se o texto digitado em um campo é igual ao texto esperado.
        
        Args:
            xpath (str): O XPath do elemento que deseja verificar.
            texto_esperado (str): O texto esperado.

        Returns:
            bool: True se o texto digitado for igual ao texto esperado, False caso contrário.
        '''
        try:
            valor_atual = self.obter_atributo(xpath, 'value')
            return valor_atual == texto_esperado
        except Exception as e:
            print(f"Erro ao verificar o texto digitado: {e}")
            raise
    
    def verificar_texto_selecionado(self, xpath: str, texto_esperado: str):
        '''
        Verifica se o texto atualmente selecionado em um select é igual ao texto esperado.
        
        Args:
            xpath (str): O XPath do elemento (select) que deseja verificar.
            texto_esperado (str): O texto esperado.
        
        Returns:
            bool: True se o texto atualmente selecionado for igual ao texto esperado, False caso contrário.
        '''
        try:
            texto_atual = self.obter_texto_selecionado(xpath)
            return texto_atual == texto_esperado
        except Exception as e:
            print(f"Erro ao verificar o select: {e}")
            raise
    
    def obter_texto_selecionado(self, xpath: str):
        '''
        Obtém o texto atualmente selecionado em um elemento select.
        
        Args:
            xpath (str): O XPath do elemento (select) que deseja obter o texto selecionado.
        
        Returns:
            str: O texto atualmente selecionado no select.
        '''
        try:
            elemento = self.wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
            selecao = Select(elemento)
            opcao_selecionada = selecao.first_selected_option
            return opcao_selecionada.text
        except Exception as e:
            print(f"Erro ao obter o texto do select: {e}")
            raise

### MANIPULAÇÃO DE ARQUIVOS

def selecionar_arquivo(titulo="Selecione um arquivo", tipos_arquivos=[("Todos os arquivos", "*.*")]):
    
    '''
    Abre uma janela para o usuário escolher um arquivo.

    Args:
        titulo (str): O cabeçalho da janela de diálogo.
        tipos_arquivos (list): Uma lista de tuplas contendo os tipos de arquivos e extensões permitidas.

    Returns:
        str: O caminho completo do arquivo selecionado ou None (se cancelado).
    '''
    try:
        caminho = filedialog.askopenfilename(
            title=titulo,
            filetypes=tipos_arquivos
        )
        return caminho if caminho else None
    except Exception as e:
        print("Erro", f"Erro ao selecionar arquivo: {e}")
        return None

def selecionar_multiplos_arquivos(titulo="Selecione os arquivos"):
    
    '''
    Permite selecionar vários arquivos de uma vez.

    Args:
        titulo (str): O cabeçalho da janela de diálogo.

    Returns:
        list: Uma lista de caminhos completos dos arquivos selecionados ou uma lista vazia (se cancelado).
    '''
    try:
        arquivos = filedialog.askopenfilenames(title=titulo)
        return list(arquivos) if arquivos else []
    except Exception as e:
        print("Erro", f"Erro ao selecionar arquivos: {e}")
        return []

def renomear_arquivo(caminho_atual, novo_nome):
    
    '''
    Renomeia um arquivo mantendo-o na mesma pasta.

    Args:
        caminho_atual (str): O caminho completo do arquivo que deseja renomear.
        novo_nome (str): O novo nome para o arquivo.

    Returns:
        str: O caminho completo do arquivo renomeado.
    '''
    try:
        diretorio = os.path.dirname(caminho_atual)
        novo_caminho = os.path.join(diretorio, novo_nome)
        
        os.rename(caminho_atual, novo_caminho)
        print(f"Arquivo renomeado para: {novo_nome}")
        return novo_caminho # Retorna o novo path para uso futuro
    except Exception as e:
        print(f"Erro ao renomear arquivo {caminho_atual}: {e}")

def mover_arquivo(origem, destino):
    
    '''
    Move um arquivo de 'origem' para 'destino'.

    Args:
        origem (str): O caminho completo do arquivo que deseja mover.
        destino (str): O caminho completo para onde o arquivo será movido.
    '''
    try:
        shutil.move(origem, destino)
        print(f"Arquivo movido de {origem} para {destino}")
    except Exception as e:
        print(f"Erro ao mover arquivo: {e}")

def copiar_arquivo(origem, destino):
    
    '''
    Copia um arquivo mantendo os metadados (datas de criação, etc).
    
    Args:
        origem (str): O caminho completo do arquivo a ser copiado.
        destino (str): O caminho completo para onde o arquivo será copiado.
    '''
    try:
        shutil.copy2(origem, destino)
        print(f"Arquivo copiado para {destino}")
    except Exception as e:
        print(f"Erro ao copiar arquivo: {e}")

def excluir_arquivo(caminho):
    
    '''
    Remove um arquivo permanentemente.
    
    Args:
        caminho (str): O caminho completo do arquivo que deseja excluir.
    '''
    try:
        if os.path.exists(caminho):
            os.remove(caminho)
            print(f"Arquivo excluído: {caminho}")
        else:
            print(f"Arquivo não encontrado para exclusão: {caminho}")
    except Exception as e:
        print(f"Erro ao excluir arquivo: {e}")

def aguardar_arquivo(caminho_arquivo: str, timeout=20):
    '''
    Aguarda até que um arquivo exista no caminho especificado ou até que o tempo limite seja atingido.

    Args:
        caminho_arquivo (str): O caminho completo do arquivo que deseja aguardar.
        timeout (int): O tempo máximo de espera em segundos. Padrão é 20 segundos.
    '''
    inicio = time.time()
    while not os.path.exists(caminho_arquivo):
        if time.time() - inicio > timeout:
            raise TimeoutError(f"O arquivo {caminho_arquivo} não foi encontrado dentro do tempo limite de {timeout} segundos.")

### GERENCIAMENTO DE PASTAS

def selecionar_pasta(titulo="Selecione uma pasta"):
    
    '''
    Abre uma janela para o usuário escolher um diretório.

    Args:
        titulo (str): O título da janela de seleção de pasta.

    Returns:
        str: O caminho completo da pasta selecionada ou None (se cancelado).
    '''
    try:
        pasta = filedialog.askdirectory(title=titulo)
        return pasta if pasta else None
    except Exception as e:
        print("Erro", f"Erro ao selecionar pasta: {e}")
        return None

def criar_pasta(caminho_pasta: str):
    
    '''
    Cria uma pasta (e subpastas se necessário).
    
    Args:
        caminho_pasta (str): O caminho completo da pasta que deseja criar.
    '''
    #exist_ok=True evita erro se a pasta já existir.'''
    try:
        os.makedirs(caminho_pasta, exist_ok=True)
        print(f"Pasta garantida: {caminho_pasta}")
    except Exception as e:
        print(f"Erro ao criar pasta: {e}")

def listar_arquivos(diretorio: str, extensao=None):
    
    '''
    Retorna uma lista com os nomes dos arquivos no diretório.

    Args:
        diretorio (str): O caminho do diretório onde deseja listar os arquivos.
        extensao (str, opcional): Se fornecido, filtra os arquivos por extensão (ex: '.pdf').
    
    Returns:
        list: Uma lista com os nomes dos arquivos encontrados no diretório (filtrados por extensão se especificado).
    '''
    try:
        arquivos = os.listdir(diretorio)
        if extensao:
            arquivos = [f for f in arquivos if f.endswith(extensao)]
        return arquivos
    except Exception as e:
        print(f"Erro ao listar arquivos em {diretorio}: {e}")
        return []

def listar_recursivo(diretorio: str, extensao=None):
    
    '''
    Lista todos os arquivos, incluindo os que estão em subpastas.
    
    Args:
        diretorio (str): O caminho do diretório onde deseja listar os arquivos.
        extensao (str, opcional): Se fornecido, filtra os arquivos por extensão.
    
    Returns:
        list: Uma lista com os caminhos completos dos arquivos encontrados no diretório e subdiretórios (filtrados por extensão se especificado).
    '''
    arquivos_encontrados = []
    try:
        for raiz, diretorios, arquivos in os.walk(diretorio):
            for arquivo in arquivos:
                if extensao is None or arquivo.endswith(extensao):
                    arquivos_encontrados.append(os.path.join(raiz, arquivo))
        return arquivos_encontrados
    except Exception as e:
        print("Erro", f"Erro na busca recursiva: {e}")
        return []

def pasta_esta_vazia(caminho_pasta: str):
    
    '''
    Verifica se uma pasta não contém arquivos ou subpastas.
    
    Args:
        caminho_pasta (str): O caminho da pasta que deseja verificar.

    Returns:
        bool: True se a pasta estiver vazia, False caso contrário.
    '''
    return not any(os.scandir(caminho_pasta))

def excluir_pasta_completa(caminho_pasta: str):
    
    '''
    Remove a pasta e todo o seu conteúdo (arquivos e subpastas).
    
    Args:
        caminho_pasta (str): O caminho da pasta que deseja excluir.
    '''
    try:
        if os.path.exists(caminho_pasta):
            shutil.rmtree(caminho_pasta)
            messagebox.showinfo("Sucesso", f"Pasta removida: {caminho_pasta}")
        else:
            messagebox.showwarning("Aviso", "Pasta não encontrada.")
    except Exception as e:
        print("Erro", f"Erro ao excluir pasta: {e}")

def compactar_para_zip(caminho_origem: str, nome_arquivo: str):
    
    '''
    Cria um arquivo .zip de uma pasta ou arquivo.
    
    Args:
        caminho_origem (str): O caminho da pasta ou arquivo que deseja compactar.
        nome_arquivo (str): O nome do arquivo .zip que deseja criar (sem extensão).
    '''
    try:
        shutil.make_archive(nome_arquivo, 'zip', caminho_origem)
        messagebox.showinfo("Sucesso", f"Arquivo {nome_arquivo}.zip criado!")
    except Exception as e:
        print("Erro", f"Erro ao compactar: {e}")

def descompactar_zip(arquivo_zip: str, caminho_destino: str):
    
    '''
    Extrai o conteúdo de um arquivo .zip.
    
    Args:
        arquivo_zip (str): O caminho completo do arquivo .zip que deseja descompactar.
        destino (str): O caminho da pasta onde o conteúdo será extraído.
    '''
    try:
        shutil.unpack_archive(arquivo_zip, caminho_destino)
        messagebox.showinfo("Sucesso", f"Extraído em: {caminho_destino}")
    except Exception as e:
        print("Erro", f"Erro ao descompactar: {e}")

### UTILITÁRIOS E VERIFICAÇÕES

def verifica_existe(caminho):
    
    '''
    Verifica se um arquivo ou pasta existe.
    
    Args:
        caminho (str): O caminho do arquivo ou pasta que deseja verificar.

    Returns:
        bool: True se o arquivo ou pasta existir, False caso contrário.
    '''
    return os.path.exists(caminho)

def obter_arquivo_mais_recente(diretorio: str, extensao=None):

    '''
    Útil para pegar o último arquivo baixado na pasta de Downloads.
    
    Args:
        diretorio (str): O caminho do diretório onde deseja buscar o arquivo.
        extensao (str, opcional): Se fornecido, filtra os arquivos por extensão (ex: '.pdf').

    Returns:
        str: O caminho completo do arquivo mais recente encontrado no diretório (filtrado por extensão se especificado).
    '''
    try:
        arquivos = listar_arquivos(diretorio, extensao)
        if not arquivos:
            return None
        
        #reconstrói os caminhos completos
        caminhos_completos = [os.path.join(diretorio, f) for f in arquivos]
        
        #retorna o arquivo com a data de modificação mais recente
        arquivo_recente = max(caminhos_completos, key=os.path.getmtime)
        return arquivo_recente
    except Exception as e:
        print(f"Erro ao buscar arquivo recente: {e}")
        return None