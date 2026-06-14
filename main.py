import random
from deap import base, creator, tools


# ---------------------------------------------------------------
# 1. Leitura do arquivo de distâncias
# ---------------------------------------------------------------
def carrega_distancias(caminho="edgesbrasil58.tsp"):
    """
    Lê a matriz triangular do arquivo e monta o dicionário de distâncias.

    OBS: as cidades são armazenadas com índices de 0 a 57 (em vez de 1 a 58),
    pois o operador de crossover cxOrdered do DEAP usa os valores do
    indivíduo diretamente como índices de lista (que vão de 0 a n-1).
    """
    distancias = {}
    with open(caminho) as objArq:
        for i in range(1, 58):  # linhas 1 a 57 (a 58 não tem arestas a listar)
            linha = objArq.readline()
            lista = linha.split()

            for j in range(i + 1, 59):  # colunas i+1 a 58
                if len(lista) > 0:
                    peso = int(lista.pop(0))
                else:
                    print(f"Erro! linha {i} do arquivo não possui elementos suficientes")
                    exit()
                # converte para indexação 0..57
                distancias[(i - 1, j - 1)] = peso
                distancias[(j - 1, i - 1)] = peso
    return distancias


NUM_CIDADES = 58
SOLUCAO_OTIMA = 25395
TOLERANCIA = 0.01  # 1%
LIMITE_ACEITAVEL = SOLUCAO_OTIMA * (1 + TOLERANCIA)

distancias = carrega_distancias()


# ---------------------------------------------------------------
# 2. Função de custo (fitness)
# ---------------------------------------------------------------
def custo_caminho(permutacao, dic_distancias=distancias):
    """Calcula a distância total da rota (incluindo o retorno à cidade inicial)."""
    soma = 0
    for i in range(len(permutacao) - 1):
        a, b = permutacao[i], permutacao[i + 1]
        if (a, b) in dic_distancias:
            soma += dic_distancias[(a, b)]
        else:
            print(f"Erro! ({a},{b}) não existe no dicionário!")
            exit()
    soma += dic_distancias[(permutacao[-1], permutacao[0])]
    return soma


def avalia(individuo):
    """Função de avaliação (fitness) chamada pelo toolbox do DEAP."""
    return (custo_caminho(individuo),)


# ---------------------------------------------------------------
# 3. Configuração do DEAP (criação dos tipos)
# ---------------------------------------------------------------
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

# indivíduo = permutação aleatória das cidades (0..57, índices da matriz de distâncias)
toolbox.register("indices", random.sample, range(0, NUM_CIDADES), NUM_CIDADES)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", avalia)
toolbox.register("mate", tools.cxOrdered)
toolbox.register("select", tools.selTournament, tournsize=2)


# ---------------------------------------------------------------
# 4. Mutação por troca (swap mutation)
# ---------------------------------------------------------------
def mutacao_swap(individuo, indpb=0.02):
    """
    Mutação por troca (swap mutation) para TSP.

    Para cada gene, com probabilidade `indpb`, sorteia uma outra posição
    aleatória do indivíduo e troca os dois valores entre si.
    """
    n = len(individuo)
    for i in range(n):
        if random.random() < indpb:
            j = random.randint(0, n - 1)
            individuo[i], individuo[j] = individuo[j], individuo[i]

    return (individuo,)


toolbox.register("mutate", mutacao_swap, indpb=0.02)


# ---------------------------------------------------------------
# 5. Busca local 2-opt (poda final)
# ---------------------------------------------------------------
def dois_opt(individuo, dic_distancias=distancias):
    """
    Busca local 2-opt: tenta inverter segmentos da rota enquanto houver
    melhora no custo total. Usada apenas no final do processo, como
    refinamento da melhor solução encontrada pelo AG.
    """
    melhor = individuo[:]
    melhor_custo = custo_caminho(melhor, dic_distancias)
    n = len(melhor)

    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                novo = melhor[:]
                novo[i + 1:j + 1] = reversed(novo[i + 1:j + 1])
                novo_custo = custo_caminho(novo, dic_distancias)
                if novo_custo < melhor_custo:
                    melhor = novo
                    melhor_custo = novo_custo
                    melhorou = True
    return melhor, melhor_custo


# ---------------------------------------------------------------
# 6. Algoritmo Genético - modelo steady-state
# ---------------------------------------------------------------
TAM_POP = 100
PROB_CROSSOVER = 0.9
PROB_MUTACAO_IND = 0.3
ELITISMO = 5
PARES_POR_ITERACAO = 5  # gera 5 pares (10 filhos) por iteração
FATOR_POP_INICIAL = 3   # gera FATOR_POP_INICIAL * TAM_POP indivíduos e seleciona os melhores


def algoritmo_genetico(max_iteracoes=2000):
    # ---- geração inicial aleatória, refinada por seleção ----
    # gera uma população maior e mantém apenas os TAM_POP melhores indivíduos,
    # garantindo que a primeira geração já comece com soluções razoáveis
    populacao_bruta = toolbox.population(n=TAM_POP * FATOR_POP_INICIAL)
    for ind in populacao_bruta:
        ind.fitness.values = toolbox.evaluate(ind)

    populacao_bruta.sort(key=lambda ind: ind.fitness.values[0])
    populacao = populacao_bruta[:TAM_POP]

    for iteracao in range(max_iteracoes):
        melhor = populacao[0]

        # critério de parada: variância máxima de 1% sobre o ótimo
        if melhor.fitness.values[0] <= LIMITE_ACEITAVEL:
            break

        # ---- gera vários pares de filhos nesta iteração ----
        for _ in range(PARES_POR_ITERACAO):
            # ---- seleção dos pais por torneio ----
            candidatos = toolbox.select(populacao, k=2)
            pai1, pai2 = (toolbox.clone(c) for c in candidatos)

            # ---- order crossover (90% de chance) ----
            if random.random() < PROB_CROSSOVER:
                filho1, filho2 = toolbox.mate(pai1, pai2)
            else:
                filho1, filho2 = pai1, pai2

            # ---- mutação por troca (30% de chance por indivíduo) ----
            for filho in (filho1, filho2):
                if random.random() < PROB_MUTACAO_IND:
                    toolbox.mutate(filho)

                # reavaliação obrigatória após cruzamento/mutação
                del filho.fitness.values
                filho.fitness.values = toolbox.evaluate(filho)

                # ---- substituição steady-state ----
                # encontra o pior indivíduo fora da faixa de elitismo
                pior_idx = max(
                    range(ELITISMO, len(populacao)),
                    key=lambda idx: populacao[idx].fitness.values[0],
                )
                if filho.fitness.values[0] < populacao[pior_idx].fitness.values[0]:
                    populacao[pior_idx] = filho
                    # mantém a população ordenada para próxima iteração
                    populacao.sort(key=lambda ind: ind.fitness.values[0])

    populacao.sort(key=lambda ind: ind.fitness.values[0])
    return populacao


# ---------------------------------------------------------------
# 7. Execução
# ---------------------------------------------------------------
if __name__ == "__main__":
    import time

    random.seed(42)

    inicio = time.time()
    populacao_final = algoritmo_genetico(max_iteracoes=2000)
    fim = time.time()

    melhor = populacao_final[0]

    rota_legivel = [cidade + 1 for cidade in melhor]  # converte 0..57 -> 1..58
    

    
    rota_refinada, custo_refinado = dois_opt(melhor, distancias)

    print(f"\n\nMenor custo (taxa fitness do melhor indíviduo): {custo_refinado}")
    rota_legivel = [cidade + 1 for cidade in rota_refinada]  # converte 0..57 -> 1..58
    print(f"\nRota (cidades 1 a 58): {rota_legivel}")
    print(f"\nSolução ótima conhecida: {SOLUCAO_OTIMA}")
    diferenca = 100 * (custo_refinado - SOLUCAO_OTIMA) / SOLUCAO_OTIMA
    print(f"\nDiferença percentual em relação ao ótimo: {diferenca:.2f}%")

    tempo_total = fim - inicio
    print(f"\nTempo de execução: {tempo_total:.2f} segundos")