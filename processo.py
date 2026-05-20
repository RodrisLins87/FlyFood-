import random

# =============================================================================
# 1. CARREGAMENTO DOS DADOS (Adaptado para o formato real do brazil58.tsp)
# =============================================================================
distancias = {}
try:
    with open("brazil58.tsp", "r") as objArq:
        # Pula o cabeçalho do arquivo .tsp até chegar na seção de pesos
        for line in objArq:
            if "EDGE_WEIGHT_SECTION" in line:
                break

        # O formato UPPER_ROW fornece as distâncias em triângulo superior
        for i in range(1, 58): 
            linha = ""
            # Garante a leitura correta mesmo se a linha lógica estiver quebrada em várias físicas
            while True:
                proxima = objArq.readline().split()
                if not proxima:
                    break
                linha += " ".join(proxima) + " "
                if len(linha.split()) >= (58 - i):
                    break
            
            lista = inline_dados = linha.split()
            for j in range(i + 1, 59):
                if lista:
                    peso = int(lista.pop(0))
                    distancias[(i, j)] = peso
                    distancias[(j, i)] = peso
    print("Arquivo 'brazil58.tsp' carregado com sucesso!\n")
except FileNotFoundError:
    print("Erro: Arquivo 'brazil58.tsp' não encontrado. Verifique o nome do arquivo no diretório.")

# =============================================================================
# 2. INICIALIZAÇÃO DA POPULAÇÃO
# =============================================================================
def inicializaPopulacao(tamanho, qtdeCidades):
    populacao = []
    rota_base = list(range(1, qtdeCidades + 1))
    for _ in range(tamanho):
        individuo = rota_base[:]
        random.shuffle(individuo)
        populacao.append(individuo)
    return populacao

# =============================================================================
# 3. FUNÇÃO DE APTIDÃO (FITNESS)
# =============================================================================
def calcular_fitness(rota, dicDistancias):
    """
    Calcula a aptidão da rota. Como queremos minimizar a distância,
    o fitness é o inverso multiplicativo da distância total (1 / distancia).
    """
    distancia_total = 0
    # Soma as distâncias entre cidades consecutivas
    for i in range(len(rota) - 1):
        distancia_total += dicDistancias[(rota[i], rota[i+1])]
    
    # Adiciona a volta da última cidade para a primeira
    distancia_total += dicDistancias[(rota[-1], rota[0])]
    
    if distancia_total == 0:
        return 0
    return 1.0 / distancia_total

# =============================================================================
# 4. OPERADOR DE CRUZAMENTO (ORDER CROSSOVER - OX)
# =============================================================================
def crossover_order(pai1, pai2):
    """
    Mantém a ordem relativa de um segmento do Pai 1 e preenche o resto com o Pai 2
    sem gerar cidades duplicadas.
    """
    tamanho = len(pai1)
    a, b = sorted(random.sample(range(tamanho), 2))
    
    filho = [None] * tamanho
    filho[a:b] = pai1[a:b] # Copia o trecho do Pai 1
    
    ponteiro = 0
    for cidade in pai2:
        if cidade not in filho:
            while filho[ponteiro] is not None:
                ponteiro += 1
            filho[ponteiro] = cidade
    return filho

# =============================================================================
# 5. OPERADOR DE MUTAÇÃO (INVERSION MUTATION)
# =============================================================================
def mutacao_inversion(rota):
    """
    Inverte a ordem das cidades em um segmento aleatório da rota.
    É o operador mutacional mais eficiente para o problema do TSP.
    """
    nova_rota = rota[:]
    idx1, idx2 = sorted(random.sample(range(len(nova_rota)), 2))
    nova_rota[idx1:idx2+1] = reversed(nova_rota[idx1:idx2+1])
    return nova_rota

def aplicar_mutacao(rota, taxa_mutacao=0.1):
    """
    Aplica a Mutação por Inversão caso o sorteio respeite a taxa estipulada.
    """
    if random.random() < taxa_mutacao:
        return mutacao_inversion(rota)
    return rota[:]

# =============================================================================
# 6. EXECUÇÃO / TESTE DOS OPERADORES
# =============================================================================
TAMANHO_POPULACAO = 100
QTDE_CIDADES = 58

# Criando a população inicial
populacao_inicial = inicializaPopulacao(TAMANHO_POPULACAO, QTDE_CIDADES)
print(f"População inicial de {len(populacao_inicial)} indivíduos criada.")

if distancias:
    # --- Demonstração prática do funcionamento dos operadores ---
    pai1 = populacao_inicial[0]
    pai2 = populacao_inicial[1]

    print("\n--- TESTE DOS OPERADORES DO PROJETO ---")
    print(f"Aptidão (Fitness) do Pai 1: {calcular_fitness(pai1, distancias):.8f}")

    # Executando Cruzamento por Ordem
    filho = crossover_order(pai1, pai2)
    print(f"Filho gerado via OX (Tamanho correto? {len(filho) == QTDE_CIDADES})")

    # Executando Mutação por Inversão (Forçando taxa de 100% apenas para o teste passar pela validação)
    filho_mutado = aplicar_mutacao(filho, taxa_mutacao=1.0)
    print(f"Filho após Mutação por Inversão (Tamanho correto? {len(filho_mutado) == QTDE_CIDADES})")