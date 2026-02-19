# AutomaWeb 🕸️📁

**AutomaWeb** é uma biblioteca Python poderosa e simplificada para automação de tarefas na web e gerenciamento de arquivos no sistema operacional. Construída sobre o Selenium e bibliotecas nativas do Python, ela remove a complexidade do código boilerplate, permitindo que você crie robôs e scripts de automação de forma rápida, legível e eficiente.

## 🚀 Instalação

Você pode instalar o AutomaWeb facilmente através do gerenciador de pacotes pip:

```bash
pip install automaweb

```

*Nota: Certifique-se de ter os navegadores (Chrome, Edge ou Firefox) instalados em sua máquina. O Selenium Manager moderno (incluído no Selenium 4+) lidará com o download automático dos drivers (como o ChromeDriver) para você.*

---

## 💡 Visão Geral e Recursos

A biblioteca é dividida em duas frentes principais:

1. **Automação Web (`Navegador`)**: Controle simplificado de navegadores (Chrome, Edge, Firefox), com métodos prontos para clicar, digitar, esperar elementos, gerenciar abas, lidar com iframes e até salvar/carregar cookies. Ele já inclui verificações embutidas e tratamento de "stuns" (tempos de espera entre ações).
2. **Gerenciamento de Arquivos e Pastas**: Funções utilitárias diretas para criar pastas, mover, copiar, renomear, excluir, compactar/descompactar (ZIP), buscar arquivos mais recentes e interagir com o usuário via interface gráfica (Tkinter) para seleção de caminhos.

---

## 🛠️ Exemplos de Uso

### 1. Automação Web Básica

```python
from automaweb import Navegador

# Inicializa o navegador Chrome com um tempo de espera (stun) de 1 segundo entre ações
nav = Navegador(tempo_stun=1, navegador="chrome")

# Abre o navegador (pode usar headless=True para rodar em segundo plano)
nav.abrir_driver(headless=False)

try:
    # Acessa um site
    nav.abrir_url("https://www.google.com")
    
    # Digita uma pesquisa e clica no botão (XPaths fictícios para exemplo)
    nav.digitar("//textarea[@title='Pesquisar']", "Automação com Python")
    nav.clicar("//input[@value='Pesquisa Google']")
    
    # Tira um print da tela
    nav.tirar_screenshot("resultado_pesquisa")

finally:
    # Garante que o navegador será fechado
    nav.fechar_driver()

```

### 2. Manipulação de Arquivos e Pastas

```python
import os
from automaweb import criar_pasta, mover_arquivo, obter_arquivo_mais_recente

caminho_downloads = f"{os.getlogin()}/Downloads"
pasta_destino = f"{caminho_downloads}/Relatorios_Processados"

# Cria a pasta se ela não existir
criar_pasta(pasta_destino)

# Pega o último PDF baixado na pasta de downloads
ultimo_pdf = obter_arquivo_mais_recente(caminho_downloads, extensao=".pdf")

if ultimo_pdf:
    # Move o arquivo para a nova pasta
    mover_arquivo(ultimo_pdf, f"{pasta_destino}/relatorio_final.pdf")
    print("Arquivo processado com sucesso!")

```

---

## 🎯 Guia Definitivo: Dominando o XPath

O **XPath** (XML Path Language) é a espinha dorsal da automação web com o AutomaWeb. Ele funciona como um "endereço" ou "caminho" para encontrar qualquer elemento dentro da estrutura HTML de uma página.

### Como encontrar o XPath de um elemento?

1. Abra o navegador e acesse a página desejada.
2. Clique com o botão direito no elemento (botão, campo de texto) e selecione **Inspecionar**.
3. O painel de Ferramentas do Desenvolvedor (DevTools) será aberto, destacando o código HTML do elemento.
4. Pressione `Ctrl + F` (ou `Cmd + F`) no DevTools para abrir a barra de busca e testar seus XPaths em tempo real.

### Regra de Ouro: Fuja do XPath Absoluto!

❌ **Absoluto:** `/html/body/div[1]/div/div[2]/form/input`
Isso quebra se o dono do site adicionar um único elemento novo na página.

✅ **Relativo:** `//input[@id='email']`
Isso busca o elemento em qualquer lugar da página que atenda aos critérios, sendo muito mais resistente a mudanças.

### Sintaxe Básica do XPath Relativo

A estrutura padrão é: `//tag[@atributo='valor']`

* **`//`**: Busca em qualquer lugar do documento.
* **`tag`**: O tipo de elemento (`input`, `button`, `div`, `a`, `*` para qualquer tag).
* **`@atributo`**: O nome do atributo HTML (`id`, `class`, `name`, `type`).
* **`'valor'`**: O valor exato do atributo.

**Exemplos:**

* `//input[@id='usuario']` (Encontra um input com o id "usuario")
* `//button[@type='submit']` (Encontra um botão de envio)
* `//*[@name='senha']` (Encontra *qualquer* elemento com o name "senha")

### Usos Avançados e Dicas Profissionais

O poder real do XPath está nas suas funções dinâmicas. Aqui estão as técnicas essenciais para automações robustas:

#### 1. Selecionando pelo Texto (`text()`)

Muitas vezes, botões ou links não têm IDs ou classes claras, mas têm um texto visível.

* **Sintaxe:** `//tag[text()='Texto Exato']`
* **Exemplo:** `//button[text()='Fazer Login']`
* **Uso no AutomaWeb:** `nav.clicar("//button[text()='Fazer Login']")`

#### 2. Busca por Texto Parcial (`contains()`)

Ideal para quando uma classe tem vários nomes (ex: `class="btn btn-primary active"`) ou o texto muda ligeiramente (ex: "Bem-vindo, João").

* **Sintaxe:** `//tag[contains(@atributo, 'parte_do_valor')]`
* **Sintaxe (Texto):** `//tag[contains(text(), 'parte_do_texto')]`
* **Exemplos:**
* `//div[contains(@class, 'btn-primary')]` (Pega o botão mesmo que tenha outras classes)
* `//a[contains(text(), 'Esqueci minha')]` (Clica no link "Esqueci minha senha")

#### 3. Múltiplas Condições (`and` / `or`)

Quando um único atributo não é suficiente para identificar um elemento unicamente.

* **Sintaxe:** `//tag[@attr1='val1' and @attr2='val2']`
* **Exemplo:** `//input[@type='text' and @placeholder='Digite seu CPF']`

#### 4. Navegando pela Árvore (Eixos XPath)

Às vezes, o elemento que você quer clicar não tem identificadores, mas o "pai" ou "irmão" dele tem.

* **Subindo para o elemento Pai (`/..` ou `parent::`)**
Você encontra um texto, mas quer clicar na caixa inteira que o envolve.
* `//span[text()='Opção 1']/..`


* **Buscando o próximo elemento (Irmão - `following-sibling::`)**
Você encontra a label "Nome:", e quer o campo de input que vem logo em seguida.
* `//label[text()='Nome:']/following-sibling::input`

#### Resumo de Estratégia XPath para Automações

Sempre tente usar identificadores na seguinte ordem de prioridade para evitar que seu robô quebre facilmente:

1. `@id` (Único e imutável na maioria das vezes).
2. `@name` (Geralmente único em formulários).
3. `text()` (Se o botão tiver um texto fixo).
4. `contains(@class, '...')` (Classes específicas).
5. Navegação a partir de um pai/irmão estável.

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Se você tiver ideias para melhorar a biblioteca, adicionar novos recursos ao `Navegador` ou expandir os utilitários de sistema, sinta-se à vontade para abrir uma *Issue* ou enviar um *Pull Request* no repositório oficial.
