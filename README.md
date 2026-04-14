# Projeto FlyFood 🛸📦

Repositório destinado à solução do desafio **FlyFood**, um algoritmo de otimização de rotas para drones de entrega, desenvolvido no contexto da disciplina de Algoritmos e Estruturas de Dados.

## 📝 Sobre o Projeto
Em um cenário fictício no ano de 2030, o trânsito caótico exige soluções inovadoras. A FlyFood utiliza drones para realizar múltiplas entregas em uma única viagem. O desafio consiste em encontrar a **rota de menor custo** (menor distância percorrida) para economizar a bateria do equipamento.

O problema é modelado como uma variação do **Problema do Caixeiro Viajante (TSP)**, onde o drone deve:
1. Partir do ponto de origem **R**.
2. Visitar todos os pontos de entrega (letras de A-Z).
3. Retornar ao ponto de origem **R**.

---

## 📏 Lógica e Complexidade

### Distância de Manhattan
Como o drone se desloca apenas em eixos horizontais e verticais (sem diagonais), o cálculo de distância entre dois pontos $P_1(x_1, y_1)$ e $P_2(x_2, y_2)$ é feito através da fórmula da **Distância de Manhattan**:

$$d = |x_1 - x_2| + |y_1 - y_2|$$

### O Problema do Caixeiro Viajante (TSP)
Este projeto utiliza uma abordagem de **Força Bruta** através de permutações. 
* **Vantagem**: Garante a solução 100% ótima (a menor rota absoluta).
* **Limitação**: Possui complexidade fatorial $O(n!)$. O tempo de execução cresce drasticamente com o aumento do número de pontos de entrega.

---

## 🛠️ Tecnologias
* **Linguagem:** Python 3.x
* **Módulos:** `itertools` (para geração de permutações e análise de força bruta).

---

## 📂 O Arquivo de Entrada

O algoritmo processa a cidade a partir de um arquivo de texto estruturado. A primeira linha deve conter as dimensões da matriz (Linhas e Colunas), e as linhas seguintes representam o grid da cidade.

**Exemplo do formato (`.txt`):**
```text
4 5
0 0 0 0 D
0 A 0 0 0
0 0 0 0 C
R 0 B 0 0
```

## ✒️ Autores

Projeto desenvolvido em equipe por estudantes do Bacharelado em Sistemas de Informação (**BSI**) da **UFRPE**:

* **Bruno Lins** - [GitHub](https://github.com/RodrisLins87) 
* **Guilherme Abraão** - [GitHub](https://github.com/teixeiraguilherme) 
* **Cayo Menezes** - [GitHub](https://github.com/CayoMenezes) 
* **Thyago Murillo** - [GitHub](https://github.com/ThyagomMurilo09)

---
*Projeto acadêmico para aprimoramento em Estruturas de Dados e Algoritmos.*
