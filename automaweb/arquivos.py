"""
Funções utilitárias para manipulação de arquivos e pastas do sistema operacional.
"""

import logging
import os
import shutil
import time

from tkinter import filedialog, messagebox

logger = logging.getLogger(__name__)


def selecionar_arquivo(titulo: str = "Selecione um arquivo", tipos_arquivos: list = [("Todos os arquivos", "*.*")]) -> str:
    '''
    Abre uma janela para o usuário escolher um arquivo.

    Args:
        titulo (str): O cabeçalho da janela de diálogo.
        tipos_arquivos (list): Lista de tuplas com tipos e extensões permitidos.

    Returns:
        str: O caminho completo do arquivo selecionado ou None se cancelado.
    '''
    try:
        caminho = filedialog.askopenfilename(title=titulo, filetypes=tipos_arquivos)
        return caminho if caminho else None
    except Exception as e:
        logger.error(f"Erro ao selecionar arquivo: {e}")
        return None


def selecionar_multiplos_arquivos(titulo: str = "Selecione os arquivos") -> list:
    '''
    Abre uma janela para selecionar vários arquivos.

    Args:
        titulo (str): O cabeçalho da janela de diálogo.

    Returns:
        list: Lista de caminhos completos ou lista vazia se cancelado.
    '''
    try:
        arquivos = filedialog.askopenfilenames(title=titulo)
        return list(arquivos) if arquivos else []
    except Exception as e:
        logger.error(f"Erro ao selecionar arquivos: {e}")
        return []


def renomear_arquivo(caminho_atual: str, novo_nome: str) -> str:
    '''
    Renomeia um arquivo mantendo-o na mesma pasta.

    Args:
        caminho_atual (str): O caminho completo do arquivo.
        novo_nome (str): O novo nome do arquivo.

    Returns:
        str: O novo caminho completo do arquivo.
    '''
    try:
        diretorio = os.path.dirname(caminho_atual)
        novo_caminho = os.path.join(diretorio, novo_nome)
        shutil.move(caminho_atual, novo_caminho)
        logger.info(f"Arquivo renomeado para: {novo_nome}")
        return novo_caminho
    except Exception as e:
        logger.error(f"Erro ao renomear arquivo '{caminho_atual}': {e}")


def mover_arquivo(origem: str, destino: str):
    '''
    Move um arquivo de origem para destino.

    Args:
        origem (str): O caminho completo do arquivo.
        destino (str): O caminho de destino.
    '''
    try:
        shutil.move(origem, destino)
        logger.info(f"Arquivo movido de '{origem}' para '{destino}'")
    except Exception as e:
        logger.error(f"Erro ao mover arquivo: {e}")


def copiar_arquivo(origem: str, destino: str):
    '''
    Copia um arquivo mantendo os metadados (datas de criação, etc).

    Args:
        origem (str): O caminho do arquivo a copiar.
        destino (str): O caminho de destino.
    '''
    try:
        shutil.copy2(origem, destino)
        logger.info(f"Arquivo copiado para '{destino}'")
    except Exception as e:
        logger.error(f"Erro ao copiar arquivo: {e}")


def excluir_arquivo(caminho: str):
    '''
    Remove um arquivo permanentemente.

    Args:
        caminho (str): O caminho do arquivo a excluir.
    '''
    try:
        if os.path.exists(caminho):
            os.remove(caminho)
            logger.info(f"Arquivo excluído: '{caminho}'")
        else:
            logger.warning(f"Arquivo não encontrado para exclusão: '{caminho}'")
    except Exception as e:
        logger.error(f"Erro ao excluir arquivo: {e}")


def aguardar_arquivo(caminho_arquivo: str, timeout: int = 20):
    '''
    Aguarda até que um arquivo exista ou até o tempo limite.

    Args:
        caminho_arquivo (str): O caminho do arquivo a aguardar.
        timeout (int): Tempo máximo de espera em segundos. Padrão é 20.

    Raises:
        TimeoutError: Se o arquivo não aparecer dentro do timeout.
    '''
    inicio = time.time()
    while not os.path.exists(caminho_arquivo):
        if time.time() - inicio > timeout:
            raise TimeoutError(f"O arquivo '{caminho_arquivo}' não foi encontrado em {timeout} segundos.")


def selecionar_pasta(titulo: str = "Selecione uma pasta") -> str:
    '''
    Abre uma janela para o usuário escolher um diretório.

    Args:
        titulo (str): O título da janela.

    Returns:
        str: O caminho completo da pasta ou None se cancelado.
    '''
    try:
        pasta = filedialog.askdirectory(title=titulo)
        return pasta if pasta else None
    except Exception as e:
        logger.error(f"Erro ao selecionar pasta: {e}")
        return None


def criar_pasta(caminho_pasta: str):
    '''
    Cria uma pasta e subpastas intermediárias se necessário.

    Args:
        caminho_pasta (str): O caminho da pasta a criar.
    '''
    try:
        os.makedirs(caminho_pasta, exist_ok=True)
        logger.info(f"Pasta garantida: '{caminho_pasta}'")
    except Exception as e:
        logger.error(f"Erro ao criar pasta: {e}")


def listar_arquivos(diretorio: str, extensao: str = None) -> list:
    '''
    Retorna os caminhos completos dos arquivos no diretório.

    Args:
        diretorio (str): O caminho do diretório.
        extensao (str, opcional): Filtra por extensão (ex: '.pdf').

    Returns:
        list: Caminhos completos dos arquivos encontrados.
    '''
    try:
        resultado = []
        for f in os.listdir(diretorio):
            caminho = os.path.join(diretorio, f)
            if os.path.isfile(caminho):
                if extensao is None or f.endswith(extensao):
                    resultado.append(caminho)
        return resultado
    except Exception as e:
        logger.error(f"Erro ao listar arquivos em '{diretorio}': {e}")
        return []


def listar_pastas(diretorio: str) -> list:
    '''
    Retorna os caminhos completos das subpastas no diretório.

    Args:
        diretorio (str): O caminho do diretório.

    Returns:
        list: Caminhos completos das pastas encontradas.
    '''
    try:
        resultado = []
        for f in os.listdir(diretorio):
            caminho = os.path.join(diretorio, f)
            if os.path.isdir(caminho):
                resultado.append(caminho)
        return resultado
    except Exception as e:
        logger.error(f"Erro ao listar pastas em '{diretorio}': {e}")
        return []


def listar_recursivo(diretorio: str, extensao: str = None) -> list:
    '''
    Lista todos os arquivos incluindo subpastas.

    Args:
        diretorio (str): O caminho do diretório raiz.
        extensao (str, opcional): Filtra por extensão.

    Returns:
        list: Caminhos completos dos arquivos encontrados.
    '''
    resultado = []
    try:
        for raiz, _, arquivos in os.walk(diretorio):
            for arquivo in arquivos:
                if extensao is None or arquivo.endswith(extensao):
                    resultado.append(os.path.join(raiz, arquivo))
        return resultado
    except Exception as e:
        logger.error(f"Erro na busca recursiva em '{diretorio}': {e}")
        return []


def pasta_esta_vazia(caminho_pasta: str) -> bool:
    '''
    Verifica se uma pasta não contém arquivos ou subpastas.

    Args:
        caminho_pasta (str): O caminho da pasta.

    Returns:
        bool: True se vazia, False caso contrário.
    '''
    return not any(os.scandir(caminho_pasta))


def excluir_pasta_completa(caminho_pasta: str):
    '''
    Remove a pasta e todo o seu conteúdo.

    Args:
        caminho_pasta (str): O caminho da pasta a excluir.
    '''
    try:
        if os.path.exists(caminho_pasta):
            shutil.rmtree(caminho_pasta)
            messagebox.showinfo("Sucesso", f"Pasta removida: {caminho_pasta}")
        else:
            messagebox.showwarning("Aviso", "Pasta não encontrada.")
    except Exception as e:
        logger.error(f"Erro ao excluir pasta: {e}")


def compactar_para_zip(caminho_origem: str, nome_arquivo: str):
    '''
    Cria um arquivo .zip a partir de uma pasta ou arquivo.

    Args:
        caminho_origem (str): O caminho da origem a compactar.
        nome_arquivo (str): O nome do arquivo .zip (sem extensão).
    '''
    try:
        shutil.make_archive(nome_arquivo, 'zip', caminho_origem)
        messagebox.showinfo("Sucesso", f"Arquivo {nome_arquivo}.zip criado!")
    except Exception as e:
        logger.error(f"Erro ao compactar: {e}")


def descompactar_zip(arquivo_zip: str, caminho_destino: str):
    '''
    Extrai o conteúdo de um arquivo .zip.

    Args:
        arquivo_zip (str): O caminho do arquivo .zip.
        caminho_destino (str): O caminho onde o conteúdo será extraído.
    '''
    try:
        shutil.unpack_archive(arquivo_zip, caminho_destino)
        messagebox.showinfo("Sucesso", f"Extraído em: {caminho_destino}")
    except Exception as e:
        logger.error(f"Erro ao descompactar: {e}")


def verifica_existe(caminho: str) -> bool:
    '''
    Verifica se um arquivo ou pasta existe.

    Args:
        caminho (str): O caminho a verificar.

    Returns:
        bool: True se existir, False caso contrário.
    '''
    return os.path.exists(caminho)


def obter_arquivo_mais_recente(diretorio: str, extensao: str = None) -> str:
    '''
    Retorna o caminho do arquivo mais recente no diretório.
    Útil para pegar o último arquivo baixado na pasta Downloads.

    Args:
        diretorio (str): O caminho do diretório.
        extensao (str, opcional): Filtra por extensão (ex: '.pdf').

    Returns:
        str: Caminho completo do arquivo mais recente ou None se não encontrado.
    '''
    try:
        arquivos = listar_arquivos(diretorio, extensao)
        if not arquivos:
            return None
        return max(arquivos, key=os.path.getmtime)
    except Exception as e:
        logger.error(f"Erro ao buscar arquivo mais recente: {e}")
        return None
