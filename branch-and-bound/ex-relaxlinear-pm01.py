# UFC/DEMA/Programacao Inteira, 2023.1
# 
# Versao incompleta do algoritmo de branch-and-bound para o
# problema da mochila 0-1.
# 
# Exercicio: Execute o codigo e familiarize-se com o
# funcionamento dele. Tente altera-lo para que ele armazene a
# melhor solucao inteira obtida durante o processo, e apresente
# esta solucao ao final.
import graphviz as gv

# Algoritmo guloso para a relaxacao linear do problema da mochila 0-1
def RelaxacaoLinearMochila01(lucros, pesos, capacidade, varfixas=dict()):

    TOL = 1e-6
    n = len(lucros)

    b = 0 # capacidade ja utilizada
    sol = dict() # solucao parcial da relaxao linear
    vfobj = 0    # valor da funcao objetivo
    indices = list(range(n)) # indices de variaveis livres
    
    # Se existem variaveis fixas, atualizamos a solucao e a fcao obj.
    if len(varfixas) > 0:
        for (i,val) in varfixas.items():
            if val > TOL:
                b += val*pesos[i]
                sol[i] = val
                vfobj += val*lucros[i]
            indices.remove(i)
    
    if b > capacidade:
        return (vfobj, sol, False)
    
    criterio = [(lucros[i]/pesos[i], i) for i in indices]
    criterio.sort(key=lambda x: x[0], reverse=True)
    
    for (f,i) in criterio:
        if b + pesos[i] <= capacidade:
            sol[i] = 1
            vfobj += lucros[i]
            b += pesos[i]
        elif capacidade > b + TOL:
            sol[i] = (capacidade-b)/pesos[i]
            vfobj += lucros[i]*sol[i]
            b = capacidade
            return (vfobj, sol, True)
            break
    
    return (vfobj, sol, True)

def nome(d):
    s = '_'
    for ch,val in d.items():
        s += str(ch) + str(val)
    return s

#---------------------------------------------------------------------
# Exemplo de problema da mochila 0-1
L = [45, 48, 35, 51, 21]
P = [5, 8, 3, 5, 3]
C = 12

n = len(L)
TOL = 1e-6

Pilha = [ dict() ]

MSI = None
numNos = 0

arvore = gv.Digraph('bab', filename='bab-m01.gv')
print("Legenda da arvore:")
print("\tVermelho: subproblema inviavel;")
print("\tAmarelo: subproblema podado por nao-otimalidade;")
print("\tVerde: solucao inteira dominada pela incumbente;")
print("\tAzul: nova incumbente obtida via heuristica;")
print("\tCirculo vazado: solucao nao inteira, viavel e nao podada;")
print("\tRetangulo: nova solucao inteira incumbente.")


while len(Pilha) > 0:
    
    # Obter o problema subproblema a ser resolvido
    atual = Pilha.pop()

    numNos += 1

    # Resolver a relaxacao do subproblema
    (zRL, solRL, viavelRL) = RelaxacaoLinearMochila01(L, P, C, atual)
    
    # Se o subproblema e' inviavel, ignore-o e siga para o proximo
    if viavelRL == False:
        arvore.node(f"no{nome(atual)}", shape="point", color="red")
        continue
    elif MSI != None and zRL < MSI['z']:
        arvore.node(f"no{nome(atual)}", shape="point", color="yellow")
        continue

    # Detectar se existe alguma variavel com valor fracionario
    varRamificacao = None
    for i in range(n):
        if i in solRL and TOL < solRL[i] < 1.0 - TOL:
            varRamificacao = i
            break

    # Se a solucao da relaxacao e' inteira, regozije-se!
    if varRamificacao == None:
        if MSI == None or zRL > MSI['z']:
            MSI = {'z': zRL, 'x': solRL}
            arvore.node(f"no{nome(atual)}", shape="rectangle", label=f"{zRL}")
        else:
            arvore.node(f"no{nome(atual)}", shape="point", color="green")

    else: # Se a solucao nao e' inteira, siga dividindo

        # Introduzimos aqui um codigo para produzir uma solucao inteira a partir
        # da solucao relaxada. No caso particular do PM01, e' muito simples fazer
        # isso: e' suficiente zerar a unica variavel fracionaria. O intuito com
        # esta acao e' melhorar a solucao incumbente, criando a possibilidade de
        # produzir uma solucao otima ou acentuar a poda por nao-otimalidade.
        solRLb = solRL.copy()
        zRLb = zRL - solRL[varRamificacao]*L[varRamificacao]
        solRLb[varRamificacao] = 0
        if MSI == None or zRLb > MSI['z']:
            MSI = {'z': zRLb, 'x': solRLb}
            arvore.node(f"no{nome(atual)}", shape="point", fillcolor="blue")
        else:
            arvore.node(f"no{nome(atual)}", shape="point", fillcolor="white")

        fixaem0 = dict(atual)
        fixaem0[varRamificacao] = 0

        fixaem1 = dict(atual)
        fixaem1[varRamificacao] = 1

        # Anexar aa lista de subproblemas a resolver
        Pilha.append(fixaem1)
        Pilha.append(fixaem0)
        
        arvore.edge(f"no{nome(atual)}", f"no{nome(fixaem0)}")
        arvore.edge(f"no{nome(atual)}", f"no{nome(fixaem1)}")
        
arvore.view()
print(MSI)
print(numNos)
