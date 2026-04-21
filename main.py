from itertools import permutations #Importa a função de permutação
from functions import simular_dist #Importa a função que calcula a distância
import time 

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

menor_distancia = float("inf") #Pior caso
melhor_rota = None

inicio = time.time()

for ordem in permutations(cidades): #Usamos a função importada para permutar e conseguir todas as ordens possíveis das cidades
    distancia_total = 0 #Toda vez que inicia-se uma nova rota, a distância tem que ser zerada 
    
#Bloco da origem para primeira cidade da ordem 

    distancia_total += simular_dist(
    origem,
    coordenadas[ordem[0]]
)
    
#Bloco das cidades consecutivas 

    for i in range(len(ordem) - 1):
        distancia_total += simular_dist(
            coordenadas[ordem[i]], #Atual cidade
            coordenadas[ordem[i+1]] #Próxima cidade
        )
    
#Voltando para origem

    distancia_total += simular_dist(
    coordenadas[ordem[-1]], #Última cidade 
    origem
)
    
    
    if distancia_total < menor_distancia: #Verifica se a rota atual é menor que a menor rota já encontrada
        menor_distancia = distancia_total #Se for, substitui pela nova rota
        melhor_rota = ordem #E salva a ordem desta permutação na variável melhor rota

fim = time.time()
tempo_total = fim - inicio

print("Melhor rota:", ("R",) + melhor_rota + ("R",))
print("Menor distância:", menor_distancia)
print(f"Tempo de execução: {tempo_total:.4f} segundos")
print(f"Tempo: {tempo_total/60:.2f} minutos")

  