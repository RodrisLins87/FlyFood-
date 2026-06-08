import random
import time
import sys
import numpy as np #Garante reprodutibilidade 


from deap import base, creator, tools #Framework evolutivo

# =============================================================================
# 1. CARREGAMENTO DA MATRIZ DE DISTÂNCIAS (UPPER_ROW - Brazil13)
# =============================================================================
distancias = {} #Declara dicionário 
todos_valores = [] #Declara lista 

 
 #Abre o arquivo em modo leitura(que contém as distâncias entre cidades no formato UPPER_ROW)
with open("brazil58.tsp", "r") as objArq:
    for line in objArq: #Esse for percorre os valores e os adiciona na lista "todos_valores"
        line = line.strip()
        if not line or "NAME" in line or "TYPE" in line or "COMMENT" in line or "DIMENSION" in line or "EDGE_WEIGHT" in line:
            continue
        if line == "EOF":
            break
        todos_valores.extend(line.split())

n = 13 #Caso para comparação de teste, só lê as 13 primeiras cidades 
idx = 0

#Preenche o dicionário 

for i in range(1, n + 1): #Percorre "indo" i-->j
    distancias[(i, i)] = 0
    for j in range(i + 1, n + 1): #Percorre "voltando" j-->i
        if idx < len(todos_valores):
            peso = int(todos_valores[idx])
            idx += 1
        else:
            peso = 0
        distancias[(i, j)] = peso #A distância de i-->j ou j--> é a mesma
        distancias[(j, i)] = peso

print(f"Sucesso: Matriz de distâncias para {n} cidades carregada corretamente!\n")

# =============================================================================
# 2. FUNÇÕES AUXILIARES
# =============================================================================
def calcular_distancia_rota(rota):
    """Soma todas as distâncias entre as cidades da rota e volta a origem"""
    total = sum(distancias[(rota[i], rota[i + 1])] for i in range(len(rota) - 1))
    total += distancias[(rota[-1], rota[0])]
    return total


def canonizar_rota(rota): #começa pela menor cidade, e o segundo elemento é menor que o último
    """Evita contar a mesma rota duas vezes com pontos de partidas diferentes"""
    idx_min = rota.index(min(rota))
    rota = rota[idx_min:] + rota[:idx_min]
    if len(rota) > 1 and rota[1] > rota[-1]:
        rota = [rota[0]] + rota[1:][::-1]
    return rota


def normalizar_para_origem(rota, origem):
    """Usa 'canonizar_rota' e depois rotaciona a rota para que ela comece 
    pela cidade sorteada como origem, útil só para a exibição final."""
    rota_canon = canonizar_rota(rota)
    idx = rota_canon.index(origem)
    return rota_canon[idx:] + rota_canon[:idx]


# =============================================================================
# 3. CONFIGURAÇÃO DO DEAP
# =============================================================================
if hasattr(creator, "minTourLength"):
    del creator.minTourLength
if hasattr(creator, "Individual"):
    del creator.Individual

creator.create("minTourLength", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.minTourLength)

toolbox = base.Toolbox()

cidades_lista = list(range(1, n + 1))
toolbox.register("indices", random.sample, cidades_lista, n)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def avaliar(individual):
    return (calcular_distancia_rota(individual),)


def ox_crossover(ind1, ind2):
    size = len(ind1)
    a, b = sorted(random.sample(range(size), 2))

    filho1 = [None] * size
    filho1[a:b] = ind1[a:b]
    pos = b
    for item in ind2[b:] + ind2[:b]:
        if item not in filho1:
            if pos >= size: pos = 0
            filho1[pos] = item
            pos += 1

    filho2 = [None] * size
    filho2[a:b] = ind2[a:b]
    pos = b
    for item in ind1[b:] + ind1[:b]:
        if item not in filho2:
            if pos >= size: pos = 0
            filho2[pos] = item
            pos += 1

    ind1[:] = filho1
    ind2[:] = filho2
    return ind1, ind2


toolbox.register("evaluate", avaliar)
toolbox.register("mate",    ox_crossover)
toolbox.register("mutate",  tools.mutShuffleIndexes, indpb=0.02)
toolbox.register("select",  tools.selTournament, tournsize=3)


# =============================================================================
# 4. PARÂMETROS PARA 13 CIDADES
# =============================================================================
SEED        = 42
NUM_CITIES  = n
POP_SIZE    = int(NUM_CITIES * 1.5)   # ~19 indivíduos (Número de rotas na população)
CXPB        = 0.9 #90% de chance de dois indivíduos se cruzarem
MUTPB       = 0.2 #20% de chance de um indivíduo sofrer mutação
NGEN        = 1000 #Número de gerações
K_SELECTION = 750 #Quantos indivíduos são selecionados por geração


# =============================================================================
# 5. EXECUÇÃO ÚNICA COM TEMPORIZADOR
# =============================================================================
CIDADE_ORIGEM = random.choice(cidades_lista) #Cidade aleatória é escolhida como ponto de origem e retorno
print(f"Cidade de origem sorteada para o relatório: {CIDADE_ORIGEM}\n")
print("=" * 55)
print("Iniciando execução...\n")

random.seed(SEED)
np.random.seed(SEED)

populacao = toolbox.population(n=POP_SIZE)

fitnesses = list(map(toolbox.evaluate, populacao))
for ind, fit in zip(populacao, fitnesses):
    ind.fitness.values = fit

historico_media = []
historico_min   = []

inicio = time.time()

for gen in range(NGEN):
    # --- Temporizador em tempo real ---
    elapsed = time.time() - inicio
    melhor_atual = min(ind.fitness.values[0] for ind in populacao)
    sys.stdout.write(
        f"\r  Geração {gen + 1:4d}/{NGEN} | "
        f"Melhor: {melhor_atual:6} | "
        f"Tempo: {elapsed:.2f}s"
    )
    sys.stdout.flush()

    # --- Evolução ---
    offspring = toolbox.select(populacao, K_SELECTION)
    offspring = list(map(toolbox.clone, offspring))

    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    for mutant in offspring:
        if random.random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    invalidos  = [ind for ind in offspring if not ind.fitness.valid]
    fitnesses  = list(map(toolbox.evaluate, invalidos))
    for ind, fit in zip(invalidos, fitnesses):
        ind.fitness.values = fit

    populacao[:] = offspring

    fits = [ind.fitness.values[0] for ind in populacao]
    historico_media.append(sum(fits) / len(fits))
    historico_min.append(min(fits))

fim = time.time()
print()  # quebra de linha após o temporizador

# =============================================================================
# 6. RESULTADO FINAL
# =============================================================================
melhor_global    = list(tools.selBest(populacao, 1)[0])
melhor_distancia = calcular_distancia_rota(melhor_global)

rota_ordenada = normalizar_para_origem(melhor_global, CIDADE_ORIGEM)
rota_completa = rota_ordenada + [CIDADE_ORIGEM]

print("\n" + "=" * 55)
print("=== MELHOR ROTA ENCONTRADA PELO ALGORITMO ===")
print("=" * 55)
print(f"Ponto de Partida : Cidade {CIDADE_ORIGEM}")
print(f"Distância Mínima : {melhor_distancia} unidades")
print(f"Fitness da Rota  : {1 / melhor_distancia:.8f}")
print(f"Tempo de Cálculo : {fim - inicio:.4f} segundos")
print("-" * 55)
print("Fluxo do Percurso:")
print(f" 🚩 {' ➡️ '.join(map(str, rota_completa))} 🏁")
print("=" * 55)





