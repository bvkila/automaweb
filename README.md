# Automação Web & Gerenciamento de Arquivos 🚀

Esta biblioteca Python foi desenvolvida para simplificar a criação de scripts de automação, combinando o poder do **Selenium** para interações web com utilitários práticos do **Sistema Operacional** para gerenciamento de arquivos e pastas.

O objetivo é fornecer uma interface de alto nível (mais legível e menos verbosa) para tarefas comuns de RPA (Robotic Process Automation).

---

## 🛠️ Funcionalidades Principal

A biblioteca está dividida em dois pilares fundamentais:

### 1. AutomacaoWeb (Navegação)

* **Gerenciamento de Driver:** Inicialização otimizada do Microsoft Edge, incluindo suporte para modo **Headless** (segundo plano).
* **Controle de Abas:** Abertura, troca e fechamento inteligente de abas.
* **Interações Avançadas:** Cliques, digitação (com limpeza automática), Hover (passar o mouse) e seleção de dropdowns.
* **Tratamento de Esperas:** Uso nativo de `WebDriverWait` para garantir que os elementos existam antes da interação, reduzindo erros de sincronismo.
* **Captura de Tela:** Método integrado para screenshots de auditoria.
* **Suporte a Iframes:** Facilidade para entrar e sair de contextos de frames.

### 2. FileExplorer (Sistema de Arquivos)

* **Manipulação de Arquivos:** Mover, copiar, renomear e excluir arquivos com segurança.
* **Organização:** Criação de diretórios recursivos e listagem filtrada por extensão.
* **Inteligência de Download:** Função específica para localizar o arquivo mais recente em uma pasta (ideal para capturar downloads recém-concluídos).

---

## 📋 Pré-requisitos

Antes de usar, você precisará instalar as dependências necessárias:

```bash
pip install selenium

```

*Nota: Certifique-se de ter o **Microsoft Edge** instalado e o **msedgedriver** compatível com sua versão do navegador em seu PATH.*

---

## 🚀 Como Usar

Aqui está um exemplo rápido de como integrar as duas classes em um fluxo de automação:

```python
from automacao import AutomacaoWeb, FileExplorer

# 1. Iniciar a automação web
web = AutomacaoWeb()
web.iniciar_driver(headless=False)

try:
    # Navegar e realizar download (exemplo hipotético)
    web.abrir_url("https://exemplo.com/relatorios")
    web.clicar("//button[@id='download_csv']")
    
    # 2. Gerenciar o arquivo baixado
    file_sys = FileExplorer()
    downloads_path = "C:/Users/Usuario/Downloads"
    
    # Localiza o arquivo CSV mais recente
    arquivo = file_sys.obter_arquivo_mais_recente(downloads_path, extensao=".csv")
    
    if arquivo:
        file_sys.mover_arquivo(arquivo, "C:/Projeto/Dados/processar.csv")
        print("Automação concluída com sucesso!")

finally:
    web.fechar_navegador()

```

---

## 📂 Estrutura do Código

| Classe | Descrição |
| --- | --- |
| `AutomacaoWeb` | Encapsula a lógica do Selenium para interação com o DOM e o navegador. |
| `FileExplorer` | Utiliza as bibliotecas `os` e `shutil` para manipulação de arquivos locais. |

---

## 📝 Notas de Versão

* **Version 1.0:** Lançamento inicial com suporte ao Edge.
* **Tratamento de Erros:** Todos os métodos possuem blocos `try-except` para evitar interrupções abruptas e facilitar o debug via console.
