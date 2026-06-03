def simular_dist(p1, p2): #Declaração da função para simular movimentos
    x1, y1 = p1
    x2, y2 = p2

    movimentos = 0

    while x1 != x2:
        if x1 < x2:
            x1 += 1
        else:
            x1 -= 1
        movimentos += 1

    while y1 != y2:
        if y1 < y2:
            y1 += 1
        else:
            y1 -= 1
        movimentos += 1

    return movimentos

