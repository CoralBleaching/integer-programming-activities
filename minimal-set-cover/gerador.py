# Gerador de instancia de minimum set cover.
import random as rd

N = 10 # Numero de objetos
M = 7 # Numero de subconjuntos

# Semente para o gerador pseudoaleatorio
rd.seed(682)

F = []
while True:

    L = list(range(N))
    rd.shuffle(L)
    L = L[:rd.randint(1,int((N-1)*0.7))]

    F.append(L)

    if len(F) == M:
        U = set()
        for L in F:
            U.update(L)

        if len(U) == N:
            break
        else:
            F.pop(0)

with open('entrada.txt', 'w+') as arq:
    for elemento in range(N):
        texto = ''
        for subconjunto in F:
            texto += '1' if elemento in subconjunto else '0'
        arq.write(texto + '\n')
