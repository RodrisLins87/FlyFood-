import random #Importa a biblioteca de aleatoriedade 
from itertools import permutations #Importa a função de permutação

matriz=[] #Define a matriz 

#Pede o nome do arquivo que contém as informações da cidade (O arquivo tem que ser add pelo usuário no Explorador)
nome_arquivo = input("Digite o nome do arquivo: ")

with open(nome_arquivo, "r") as arquivo: #Abre o arquivo em modo leitura 
    linhas = arquivo.readlines() #Lê cada linha do arquivo e adiciona em uma lista

linhas_colunas = linhas[0].split() #No formato do arquivo, a primeira linha informa o número de colunas e linhas, ele pega a primeira linha e "quebra"
linhas_qtd = int(linhas_colunas[0]) #Transforma em inteiro a quantidade de linhas
colunas_qtd = int(linhas_colunas[1]) #Transforma em inteiro a quantidade de colunas

for linha in linhas[1:]: #Ignora a primeira linha 
    matriz.append(linha.split()) #Transforma e adiciona cada linha em uma sublista(quebrada) e adiciona na lista "matriz"

print(matriz) #imprime a matriz 

