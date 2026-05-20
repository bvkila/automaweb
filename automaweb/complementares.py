from seleniumwire import webdriver as seleniumwire_webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions

def abrir_driver_wire(self, headless: bool = False, tempo_wait: int = 10):
        '''
        Inicializa o driver com Selenium Wire para interceptação de rede.
        '''
        try:
            # Dicionário opcional para configurações específicas do Selenium Wire
            # Útil se você precisar de proxy ou ignorar erros de SSL
            sw_options = {
                'verify_ssl': False, # Frequentemente necessário para interceptar HTTPS sem erros
            }

            if self.navegador in ["chrome", "edge"]:
                if self.navegador == "chrome":
                    options = ChromeOptions()
                else:
                    options = EdgeOptions()

                # Configurações anti-detecção e log (mantidas do seu original)
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('excludeSwitches', ['enable-logging'])
                options.add_experimental_option('useAutomationExtension', False)
                options.add_argument("--log-level=3")
                options.add_argument("--start-maximized")
                
                if headless:
                    options.add_argument("--headless=new")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")

                # Inicialização usando seleniumwire.webdriver
                if self.navegador == "chrome":
                    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
                    self.driver = seleniumwire_webdriver.Chrome(options=options, seleniumwire_options=sw_options)
                else:
                    self.driver = seleniumwire_webdriver.Edge(options=options, seleniumwire_options=sw_options)

            elif self.navegador == "firefox":
                options = FirefoxOptions()
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference("useAutomationExtension", False)
                options.log.level = "fatal"
                
                if headless:
                    options.add_argument("-headless")
                
                # Inicialização usando seleniumwire.webdriver
                self.driver = seleniumwire_webdriver.Firefox(options=options, seleniumwire_options=sw_options)
            
            else:
                raise ValueError(f"Navegador '{self.navegador}' não suportado.")

            # Configurações globais
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, tempo_wait)

        except Exception as e:
            print(f"Erro ao iniciar o driver com Selenium Wire ({self.navegador}): {e}")
            raise