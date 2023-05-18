# UFC/DEMA/Programacao Inteira, 2023.1
# 
# Versao incompleta do algoritmo de branch-and-bound para o
# problema da mochila 0-1.
# 
# Exercicio: Execute o codigo e familiarize-se com o
# funcionamento dele. Tente altera-lo para que ele armazene a
# melhor solucao inteira obtida durante o processo, e apresente
# esta solucao ao final.

def relaxacao_linear_mochila(lucros: list[int] | list[float], 
                             pesos: list[int] | list[float], 
                             capacidade: int, 
                             varfixas: dict[int, float] | None = None,
                             tolerancia: float = 1e-6):
    '''Algoritmo guloso para a relaxacao linear do problema da mochila 0-1'''
    n = len(lucros)

    b = 0 # capacidade ja utilizada
    sol: dict[int, float] = dict() # solucao parcial da relaxao linear
    vfobj = 0.    # valor da funcao objetivo
    indices = list(range(n)) # indices de variaveis livres
    
    # Se existem variaveis fixas, atualizamos a solucao e a fcao obj.
    if varfixas is not None and len(varfixas) > 0:
        for i,val in varfixas.items():
            if val > tolerancia:
                b += val*pesos[i]
                sol[i] = val
                vfobj += val*lucros[i]
            indices.remove(i)
    
    if b > capacidade:
        return vfobj, sol, bool(False)
    
    criterio = [(lucros[i]/pesos[i], i) for i in indices]
    criterio.sort(key=lambda x: x[0], reverse=True)
    
    for _,i in criterio:
        if b + pesos[i] <= capacidade:
            sol[i] = 1
            vfobj += lucros[i]
            b += pesos[i]
        elif capacidade > b + tolerancia:
            sol[i] = (capacidade-b)/pesos[i]
            vfobj += lucros[i]*sol[i]
            b = capacidade
            break
    
    return vfobj, sol, bool(True)


def branch_and_bound_mochila(lucros: list[int] | list[float],
                             pesos: list[int] | list[float],
                             capacidade: int,
                             verbose: bool=False,
                             tolerancia: float = 1e-6):
    pilha: list[dict[int, float]] = [ dict() ]
    melhor: tuple[float, dict[int, float]] = (-1., {})

    while len(pilha) > 0:
        # Obter o problema subproblema a ser resolvido
        atual = pilha.pop()

        # Resolver a relaxacao do subproblema
        z_RL, sol_RL, viavel_RL = relaxacao_linear_mochila(lucros, pesos, capacidade, 
                                                             atual,tolerancia)
        
        # Se o subproblema e' inviavel, ignore-o e siga para o proximo
        if not viavel_RL:
            continue
        elif verbose: 
            print(sol_RL)

        # Detectar se existe alguma variavel com valor fracionario
        variavel_de_ramificacao = -1
        for i in range(len(lucros)):
            if i in sol_RL and tolerancia < sol_RL[i] < 1.0 - tolerancia:
                variavel_de_ramificacao = i
                break

        # Se a solucao da relaxacao e' inteira, regozije-se!
        if variavel_de_ramificacao == -1:
            if z_RL > melhor[0]:
                melhor = (z_RL, sol_RL)
            if verbose:
                print(z_RL, sol_RL)

        else: # Se a solucao nao e' inteira, siga dividindo

            fixa_em_0 = dict(atual)
            fixa_em_0[variavel_de_ramificacao] = 0

            fixa_em_1 = dict(atual)
            fixa_em_1[variavel_de_ramificacao] = 1

            # Anexar aa lista de subproblemas a resolver
            pilha.append(fixa_em_0)
            pilha.append(fixa_em_1)
    
    return melhor

def main():
    # Exemplo de problema da mochila 0-1
    L = [45, 48, 35, 51, 21]
    P = [5, 8, 3, 5, 3]
    C = 12

    print('melhor:\nobj: {}\nsolução: {}'.format(
        *branch_and_bound_mochila(L, P, C, verbose=True)))
    
if __name__ == '__main__':
    main()