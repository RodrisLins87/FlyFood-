import random

# --- CARREGAMENTO DOS DADOS ---
def carregar_dados():
    try:
        objArq = open("brazil58.tsp", "r")
        for line in objArq:
            if "EDGE_WEIGHT_SECTION" in line: break
        distancias = {}
        data = []
        for line in objArq:
            data.extend(line.split())
        objArq.close()
        
        ptr = 0
        for i in range(1, 58):
            for j in range(i + 1, 59):
                peso = int(data[ptr])
                distancias[(i, j)] = peso
                distancias[(j, i)] = peso
                ptr += 1
        return distancias
    except:
        return None

def custoCaminho(permutacao, dicDistancias):
    soma = 0
    for i in range(len(permutacao)-1):
        soma += dicDistancias[(permutacao[i], permutacao[i+1])]
    soma += dicDistancias[(permutacao[-1], permutacao[0])]
    return soma

def two_opt_agressivo(rota, dicDistancias):
    """Busca local que insiste até limpar todos os cruzamentos."""
    melhor_rota = rota[:]
    melhor_custo = custoCaminho(melhor_rota, dicDistancias)
    melhorou = True
    while melhorou:
        melhorou = False
        for i in range(1, len(melhor_rota) - 2):
            for j in range(i + 1, len(melhor_rota)):
                # Inversão do segmento i:j
                nova_rota = melhor_rota[:i] + melhor_rota[i:j][::-1] + melhor_rota[j:]
                novo_custo = custoCaminho(nova_rota, dicDistancias)
                if novo_custo < melhor_custo:
                    melhor_rota = nova_rota
                    melhor_custo = novo_custo
                    melhorou = True
                    break # First Improvement
            if melhorou: break
    return melhor_rota

def crossover_ox(pai1, pai2):
    tamanho = len(pai1)
    a, b = sorted(random.sample(range(tamanho), 2))
    filho = [None] * tamanho
    filho[a:b] = pai1[a:b]
    ptr = 0
    for cidade in pai2:
        if cidade not in filho:
            while filho[ptr] is not None: ptr += 1
            filho[ptr] = cidade
    return filho

# --- ALGORITMO GENÉTICO REFINADO ---

def resolver_brasil58_agressivo(distancias, tam_pop=50, geracoes=350):
    # Inicialização: 30% da população já começa com busca local
    populacao = []
    for _ in range(tam_pop):
        ind = list(range(1, 59))
        random.shuffle(ind)
        if random.random() < 0.3:
            ind = two_opt_agressivo(ind, distancias)
        populacao.append(ind)

    melhor_global = None
    menor_custo_global = float('inf')

    for g in range(geracoes):
        populacao.sort(key=lambda ind: custoCaminho(ind, distancias))
        
        if custoCaminho(populacao[0], distancias) < menor_custo_global:
            menor_custo_global = custoCaminho(populacao[0], distancias)
            melhor_global = populacao[0][:]

        # Elitismo: Mantém os 2 melhores intactos
        nova_pop = [populacao[0][:], populacao[1][:]]

        while len(nova_pop) < tam_pop:
            # Torneio focado no topo da tabela (K=3 entre os 20 melhores)
            p1 = min(random.sample(populacao[:20], 3), key=lambda x: custoCaminho(x, distancias))
            p2 = min(random.sample(populacao[:20], 3), key=lambda x: custoCaminho(x, distancias))
            
            filho = crossover_ox(p1, p2)
            
            # Mutação por Inversão (mais agressiva que Swap)
            if random.random() < 0.15:
                a, b = sorted(random.sample(range(58), 2))
                filho[a:b] = filho[a:b][::-1]
            
            # Busca Local em 15% dos filhos
            if random.random() < 0.15:
                filho = two_opt_agressivo(filho, distancias)
                
            nova_pop.append(filho)
        
        populacao = nova_pop

        if g % 50 == 0:
            # Refino extra no líder para garantir a descida
            populacao[0] = two_opt_agressivo(populacao[0], distancias)
            print(f"Geração {g} | Melhor Custo: {menor_custo_global}")

    # Lapidação Final Exaustiva
    resultado_final = two_opt_agressivo(melhor_global, distancias)
    print(f"\n--- RESULTADO FINAL ---")
    print(f"Custo alcançado: {custoCaminho(resultado_final, distancias)}")
    return resultado_final

# Execução
dist = carregar_dados()
if dist:
    resolver_brasil58_agressivo(dist)