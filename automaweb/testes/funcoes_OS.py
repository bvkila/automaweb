import sys
import os

diretorio_atual = os.path.dirname(os.path.abspath(__file__))
diretorio_pai = os.path.dirname(diretorio_atual)
sys.path.append(diretorio_pai)

from main import *

# arquivo = automaweb.selecionar_arquivo()
# print(arquivo)

# print("\n----------\n")

# arquivos = automaweb.selecionar_multiplos_arquivos()
# for arquivos in arquivos:
#     print(arquivos)

# print("\n----------\n")

pasta = selecionar_pasta()

pastas = listar_pastas(pasta)
for pasta in pastas:
    print(f'\npasta: {pasta}')
    arquivos = listar_arquivos(pasta)
    for arquivos in arquivos:
        print(arquivos)

print("\n----------\n")

# arquivos_2 = automaweb.listar_recursivo(pasta)
# for arquivos in arquivos_2:
#     print(arquivos)

