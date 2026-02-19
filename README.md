# 🤖 Biblioteca de Automação Web e Gerenciamento de Arquivos

Uma biblioteca Python robusta e simplificada para automatizar interações na web usando Selenium (focada no Microsoft Edge) e gerenciar arquivos/pastas no sistema operacional.

Ideal para criar robôs de extração de dados (Web Scraping), automação de rotinas de escritório, testes automatizados e organização de diretórios.

---

## 📦 Requisitos e Instalação

Para utilizar esta biblioteca, você precisará do Python instalado e de algumas dependências externas. Grande parte das bibliotecas utilizadas (`os`, `shutil`, `time`, `json`, `tkinter`, `functools`, `datetime`) já são nativas do Python.

Você só precisa instalar o Selenium:

```bash
pip install selenium

```

> **Nota:** Esta biblioteca está configurada por padrão para usar o **Microsoft Edge**. Certifique-se de ter o navegador Edge atualizado na sua máquina.

---

## 🚀 Como Usar (Quick Start)

Aqui está um exemplo básico de como iniciar o navegador, fazer uma pesquisa, tirar um print e manipular um arquivo recém-baixado:

```python
from sua_biblioteca import Navegador, obter_arquivo_mais_recente, criar_pasta, mover_arquivo

# 1. Inicializa o Navegador com um 'stun' (pausa) de 1 segundo entre ações
bot = Navegador(tempo_stun=1.0)
bot.abrir_driver(headless=False) # Mude para True se quiser rodar em segundo plano

# 2. Navega e Interage
bot.abrir_url("https://google.com")
bot.digitar('//textarea[@title="Pesquisar"]', "Gatos fofos")
bot.clicar('(//input[@value="Pesquisa Google"])[2]')
bot.tirar_screenshot("gatos_pesquisa")

# 3. Gerencia Arquivos
pasta_destino = "C:/MeusTestes/Gatos"
criar_pasta(pasta_destino)

arquivo_baixado = obter_arquivo_mais_recente("C:/Users/SeuUsuario/Downloads", ".png")
if arquivo_baixado:
    mover_arquivo(arquivo_baixado, f"{pasta_destino}/print_gatos.png")

# 4. Encerra
bot.fechar_driver()

```

---

## 🧰 Estrutura de Funcionalidades

A biblioteca é dividida em duas frentes principais:

### 1. Classe `Navegador` (Automação Web)

Gerencia toda a sessão do navegador com proteções embutidas e esperas implícitas (WebDriverWait).

* **Controle de Sessão:** `abrir_driver()`, `fechar_driver()`, `salvar_cookies()`, `carregar_cookies()`.
* **Navegação:** `abrir_url()`, `abrir_nova_aba()`, `alternar_aba()`, `fechar_aba()`, `recarregar_driver()`.
* **Interação em Tela:** `clicar()`, `digitar()`, `limpar()`, `passar_mouse()`, `rolar_ate_elemento()`, `selecionar_texto()`, `selecionar_valor()`.
* **Extração e Verificação:** `obter_texto()`, `obter_atributo()`, `verifica_existe()`, `verifica_clicavel()`, `verifica_selecionado()`.
* **Avançado:** `entrar_iframe()`, `sair_iframe()`, `tirar_screenshot()`.

### 2. Funções Soltas (Manipulação de Arquivos e SO)

Interface amigável para comandos do sistema operacional e janelas de seleção gráfica (via `tkinter`).

* **Janelas de Seleção (Pop-ups):** `selecionar_arquivo()`, `selecionar_multiplos_arquivos()`, `selecionar_pasta()`.
* **Operações de Arquivo:** `renomear_arquivo()`, `mover_arquivo()`, `copiar_arquivo()`, `excluir_arquivo()`, `aguardar_arquivo()`.
* **Operações de Pasta:** `criar_pasta()`, `listar_arquivos()`, `listar_recursivo()`, `excluir_pasta_completa()`, `pasta_esta_vazia()`.
* **Compactação:** `compactar_para_zip()`, `descompactar_zip()`.

---

## 🎯 Guia Definitivo de XPath para Automação

Praticamente todas as funções de interação da classe `Navegador` exigem uma string `xpath`. O XPath (XML Path Language) é a linguagem usada para navegar em elementos e atributos de um documento XML ou HTML.

Dominar o XPath é o que diferencia um script frágil de uma automação à prova de falhas.

### O que NUNCA fazer

Evite usar **XPath Absoluto** (ex: `/html/body/div[2]/div[1]/form/input`). Se o desenvolvedor do site adicionar um simples `<br>` ou `<div>` novo na página, seu caminho quebra e o robô falha.

### O que fazer: XPath Relativo

Sempre use o XPath relativo, que busca o elemento com base em suas características únicas, independentemente de onde ele esteja na página. Ele sempre começa com `//`.

#### 1. Sintaxe Básica

A fórmula de ouro é: `//tag_do_elemento[@atributo="valor"]`

* **Busca por ID:** O ID deve ser único na página. É o método mais seguro.
* `//input[@id="username"]`


* **Busca por Classe:**
* `//button[@class="btn-primary login"]`


* **Busca por Name:**
* `//input[@name="password"]`



#### 2. Buscas com Texto

Às vezes, o botão não tem ID ou classe útil, mas tem um texto claro.

* **Texto Exato:** Busca um botão que o texto seja exatamente "Enviar".
* `//button[text()="Enviar"]`


* **Contém Texto (Contains):** Excelente para textos dinâmicos ou com espaços sobrando.
* `//button[contains(text(), "Enviar")]`


* **Contém em Atributo:**
* `//input[contains(@class, "btn-submit")]` (Pega o botão mesmo que a classe completa seja "btn-submit active hover").



#### 3. Combinando Condições (AND / OR)

Se um atributo só não for suficiente para isolar o elemento:

* `//input[@type="text" and @name="email"]`
* `//button[text()="Confirmar" or @id="btn-confirm"]`

#### 4. Navegando na Árvore (Eixos XPath)

Às vezes, o elemento que você quer interagir não tem nada de único, mas o elemento "pai" (acima) ou "filho" (abaixo) dele tem.

* **Indo para o Filho (Descendant):** Busca um `<a>` dentro de uma div específica.
* `//div[@id="menu-principal"]//a[text()="Contato"]`


* **Indo para o Pai (Parent):** Você acha o elemento filho e volta para o pai.
* `//span[text()="Nome de Usuário"]/parent::div`


* **Indo para o Irmão (Following-Sibling):** Muito útil em formulários onde o rótulo (label) tem o texto, e o input está logo ao lado.
* `//label[text()="CPF:"]/following-sibling::input`



### 💡 Dicas de Ouro para usar com esta biblioteca

1. **Inspecione sempre:** No navegador, aperte `F12` (Ferramentas de Desenvolvedor), clique na setinha de inspeção e clique no elemento. Na aba *Elements*, aperte `Ctrl + F` e teste seu XPath ali mesmo antes de colocar no código. O navegador vai destacar o elemento em amarelo se o XPath estiver correto.
2. **Use o `tempo_stun` com inteligência:** Sites pesados demoram a renderizar cliques. Se você toma blocos ou erros de intercepção, aumente o `tempo_stun` na inicialização da classe `Navegador(tempo_stun=1.5)` ou confie nas funções de `aguardar_elemento_sumir()`.
3. **Iframes são ilhas:** Se o XPath está certinho no F12 mas a biblioteca diz que o elemento não existe, **ele provavelmente está dentro de um Iframe**. Inspecione o elemento, suba a árvore HTML e procure por uma tag `<iframe>`. Se houver, use a função `entrar_iframe('xpath_do_iframe')` antes de tentar interagir com o elemento lá de dentro. Não esqueça de dar um `sair_iframe()` depois!

---

Gostaria de ajuda para criar um script prático usando essa biblioteca recém-documentada, ou quer que eu crie um `requirements.txt` estruturado para acompanhar este README?