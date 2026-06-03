# -*- coding: utf-8 -*-
# Adaptado para Brazil58 com matriz UPPER_ROW

import random
import time
import numpy as np
import matplotlib.pyplot as plt

from deap import base, creator, tools

# =============================================================================
# 1. CARREGAMENTO DA MATRIZ DE DISTÂNCIAS (UPPER_ROW - Brazil58)
# =============================================================================
distancias = {}
todos_valores = []

# Lendo o arquivo e guardando absolutamente todos os números em uma lista única
with open("brazil58.tsp", "r") as objArq:
    for line in objArq:
        line = line.strip()
        # Pula cabeçalhos se houver, ou linhas vazias
        if not line or "NAME" in line or "TYPE" in line or "COMMENT" in line or "DIMENSION" in line or "EDGE_WEIGHT" in line:
            continue
        if line == "EOF":
            break
        todos_valores.extend(line.split())

# Definição do número de cidades para o Brazil58
n = 58
idx = 0

# Montando a matriz espelhada a partir do formato UPPER_ROW
for i in range(1, n + 1):
    distancias[(i, i)] = 0  # Distância de uma cidade para ela mesma é zero
    for j in range(i + 1, n + 1):
        if idx < len(todos_valores):
            peso = int(todos_valores[idx])
            idx += 1
        else:
            peso = 0  # Prevenção caso o arquivo venha incompleto ou menor
        distancias[(i, j)] = peso
        distancias[(j, i)] = peso

print(f"Sucesso: Matriz de distâncias para {n} cidades carregada corretamente!\n")

# =============================================================================
# 2. FUNÇÕES AUXILIARES
# =============================================================================
def calcular_distancia_rota(rota):
    """Distância total do ciclo (fecha na cidade de origem)."""
    total = sum(distancias[(rota[i], rota[i + 1])] for i in range(len(rota) - 1))
    total += distancias[(rota[-1], rota[0])]
    return total


def canonizar_rota(rota):
    """
    Normaliza o ciclo para representação única:
    1) Cidade de menor índice vai para a posição 0
    2) Sentido fixo: segundo elemento sempre menor que o último
    """
    idx_min = rota.index(min(rota))
    rota = rota[idx_min:] + rota[:idx_min]
    if len(rota) > 1 and rota[1] > rota[-1]:
        rota = [rota[0]] + rota[1:][::-1]
    return rota


def normalizar_para_origem(rota, origem):
    """Rotaciona o ciclo canonizado para começar na cidade de origem."""
    rota_canon = canonizar_rota(rota)
    idx = rota_canon.index(origem)
    return rota_canon[idx:] + rota_canon[:idx]


# =============================================================================
# 3. CONFIGURAÇÃO DO DEAP
# =============================================================================

# Limpa registros antigos caso rode em ambiente interativo (como Jupyter)
if hasattr(creator, "minTourLength"):
    del creator.minTourLength
if hasattr(creator, "Individual"):
    del creator.Individual

# Minimizar distância total (weight = -1.0)
creator.create("minTourLength", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.minTourLength)

toolbox = base.Toolbox()

# Cidades numeradas de 1 a 58
cidades_lista = list(range(1, n + 1))
toolbox.register("indices", random.sample, cidades_lista, n)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


def avaliar(individual):
    """Função de avaliação: distância total do ciclo."""
    return (calcular_distancia_rota(individual),)


def ox_crossover(ind1, ind2):
    """Order Crossover (OX) implementado manualmente — compatível com DEAP 1.4."""
    size = len(ind1)
    a, b = sorted(random.sample(range(size), 2))

    # Filho 1: segmento de ind1, resto na ordem de ind2
    filho1 = [None] * size
    filho1[a:b] = ind1[a:b]
    pos = b
    for cidade in ind2[b:] + ind2[:b]:
        if cidade not in filho1:
            if pos >= size:
                pos = 0
            filho1[pos] = cidade
            pos += 1

    # Filho 2: segmento de ind2, resto na ordem de ind1
    filho2 = [None] * size
    filho2[a:b] = ind2[a:b]
    pos = b
    for cidade in ind1[b:] + ind1[:b]:
        if cidade not in filho2:
            if pos >= size:
                pos = 0
            filho2[pos] = cidade
            pos += 1

    ind1[:] = filho1
    ind2[:] = filho2
    return ind1, ind2


toolbox.register("evaluate", avaliar)
toolbox.register("mate",    ox_crossover)                             # Crossover OX manual
toolbox.register("mutate",  tools.mutShuffleIndexes, indpb=0.02)      # Mutação por shuffle
toolbox.register("select",  tools.selTournament, tournsize=3)         # Torneio de tamanho 3


# =============================================================================
# 4. PARÂMETROS OTIMIZADOS PARA 58 CIDADES
# =============================================================================
SEED               = 42       
NUM_CITIES         = n
POP_SIZE           = 200       # População maior para expandir a diversidade genética
CXPB               = 0.9      # Probabilidade de crossover
MUTPB              = 0.2      # Probabilidade de mutação
NGEN               = 2000      # Mais gerações para dar tempo de convergir no espaço 58!
K_SELECTION        = 150       # Tamanho do pool de seleção ajustado à população
NUM_EXECUCOES      = 5         # Quantidade de testes independentes


# =============================================================================
# 5. EXECUÇÃO
# =============================================================================
def executar_uma_vez(seed_offset=0):
    random.seed(SEED + seed_offset)
    np.random.seed(SEED + seed_offset)

    populacao = toolbox.population(n=POP_SIZE)

    # Avalia população inicial
    fitnesses = list(map(toolbox.evaluate, populacao))
    for ind, fit in zip(populacao, fitnesses):
        ind.fitness.values = fit

    historico_media = []
    historico_min   = []

    for gen in range(NGEN):

        # Seleção
        offspring = toolbox.select(populacao, K_SELECTION)
        offspring = list(map(toolbox.clone, offspring))

        # Crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                del child1.fitness.values
                del child2.fitness.values

        # Mutação
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Reavalia inválidos
        invalidos = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses  = list(map(toolbox.evaluate, invalidos))
        for ind, fit in zip(invalidos, fitnesses):
            ind.fitness.values = fit

        # Substitui população
        populacao[:] = offspring

        fits = [ind.fitness.values[0] for ind in populacao]
        historico_media.append(sum(fits) / len(fits))
        historico_min.append(min(fits))

    melhor = tools.selBest(populacao, 1)[0]
    return melhor, historico_media, historico_min


# =============================================================================
# 6. MÚLTIPLAS EXECUÇÕES
# =============================================================================
CIDADE_ORIGEM = random.choice(cidades_lista)   # Sorteia uma das 58 cidades mapeadas
print(f"Cidade de origem sorteada: {CIDADE_ORIGEM}\n")
print("=" * 55)

melhor_global       = None
melhor_distancia    = float("inf")
melhor_historico_media = []
melhor_historico_min   = []

inicio = time.time()

for execucao in range(NUM_EXECUCOES):
    rota, hist_media, hist_min = executar_uma_vez(seed_offset=execucao)
    dist = calcular_distancia_rota(rota)
    print(f"Execução {execucao + 1:2d} | Distância: {dist:6} | Fitness: {1/dist:.8f}")

    if dist < melhor_distancia:
        melhor_distancia       = dist
        melhor_global          = list(rota)
        melhor_historico_media = hist_media
        melhor_historico_min   = hist_min

fim = time.time()

# =============================================================================
# 7. RESULTADO FINAL
# =============================================================================
rota_normalizada = normalizar_para_origem(melhor_global, CIDADE_ORIGEM)
rota_exibida     = rota_normalizada + [CIDADE_ORIGEM]

print("\n=== MELHOR ROTA ENCONTRADA ===")
print(f"Origem sorteada  : Cidade {CIDADE_ORIGEM}")
print(f"Rota completa    : {' -> '.join(map(str, rota_exibida))}")
print(f"Distância total  : {melhor_distancia}")
print(f"Fitness          : {1 / melhor_distancia:.8f}")
print(f"Tempo de execução: {fim - inicio:.4f} segundos")
print()
print("Parâmetros:")
print(f"  Semente (seed)         : {SEED} + offset por execução")
print(f"  Tamanho da população   : {POP_SIZE}")
print(f"  Probabilidade crossover: {CXPB}  (tipo: OX - Order Crossover)")
print(f"  Probabilidade mutação  : {MUTPB}  (tipo: Shuffle Indexes, indpb=0.02)")
print(f"  Seleção                : Torneio (tournsize=3, k={K_SELECTION})")
print(f"  Número de gerações     : {NGEN}")
print(f"  Execuções independentes: {NUM_EXECUCOES}")

# =============================================================================
# 8. GRÁFICO DE CONVERGÊNCIA
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(range(len(melhor_historico_media)), melhor_historico_media,
        "b-", label="Média da população", alpha=0.7)
ax.plot(range(len(melhor_historico_min)),  melhor_historico_min,
        "r-", label="Melhor da geração",  alpha=0.9)
ax.set_xlabel("Geração")
ax.set_ylabel("Distância total")
ax.set_title(f"Convergência do AG — Brazil58 (Melhor rota: {melhor_distancia})")
ax.legend()
plt.tight_layout()
plt.savefig("convergencia.png", dpi=150)
plt.show()
print("\nGráfico salvo em: convergencia.png")