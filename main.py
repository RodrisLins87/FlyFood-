from itertools import permutations #Importa a função de permutação
from functions import simular_dist #Importa a função que calcula a distância

matriz=[] #Define a matriz 
cidades=[] #lista que será adicionada as cidades
origem=None
coordenadas={}

#Pede o nome do arquivo que contém as informações da cidade (O arquivo tem que ser add pelo usuário no Explorador)
nome_arquivo = input("Digite o nome do arquivo: ")

with open(nome_arquivo, "r") as arquivo: #Abre o arquivo em modo leitura 
    linhas = arquivo.readlines() #Lê cada linha do arquivo e adiciona em uma lista

linhas_colunas = linhas[0].split() #No formato do arquivo, a primeira linha informa o número de colunas e linhas, ele pega a primeira linha e "quebra"
linhas_qtd = int(linhas_colunas[0]) #Transforma em inteiro a quantidade de linhas
colunas_qtd = int(linhas_colunas[1]) #Transforma em inteiro a quantidade de colunas

for linha in linhas[1:]: #Ignora a primeira linha 
    matriz.append(linha.split()) #Transforma e adiciona cada linha em uma sublista(quebrada) e adiciona na lista "matriz"


for i in range(len(matriz)): #percorre as linhas da matriz
    for j in range(len(matriz[i])): #percorre as colunas da matriz
        valor = matriz[i][j] #Atribui a coordenada (não é fixa) a uma variável

        if valor == "R": #Acha o ponto de origem e retorno e adiciona na variável "origem", que anteriormente estava vazia
            origem = (i, j)

        elif valor != "0": 
            cidades.append(valor)   
            coordenadas[valor] = (i, j)

menor_distancia = float("inf")
melhor_rota = None

for ordem in permutations(cidades):
    distancia_total = 0
    
    # origem -> primeira cidade
    distancia_total += simular_dist(
    origem,
    coordenadas[ordem[0]]
)
    

    for i in range(len(ordem) - 1):
        distancia_total += simular_dist(
            coordenadas[ordem[i]],
            coordenadas[ordem[i+1]]
        )
    
    
    distancia_total += simular_dist(
    coordenadas[ordem[-1]],
    origem
)
    
    
    if distancia_total < menor_distancia:
        menor_distancia = distancia_total
        melhor_rota = ordem

print("Melhor rota:", ("R",) + melhor_rota + ("R",))
print("Menor distância:", menor_distancia)

