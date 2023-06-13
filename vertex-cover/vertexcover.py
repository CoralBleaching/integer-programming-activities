#!pip install ortools
from ortools.linear_solver import pywraplp

def vertex_cover(grafo):
    TOL = 1.0e-6

    n = len(g)
   
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return

    solver.EnableOutput()
    
    # Criar variaveis
    x = [ solver.IntVar(0, 1, f'x{v}') for v in range(n) ]
    print('Numero de variaveis =', solver.NumVariables())

    # Restricoes
    for v1 in range(n):
        for v2 in g[v1]:
            solver.Add( x[v1] + x[v2]  >= 1 )

    print('Numero de restricoes =', solver.NumConstraints())

    # Funcao objetivo e sentido de otimizacao
    solver.Minimize( sum(x) )

    #solver.set_time_limit(5000)
    solverParams = pywraplp.MPSolverParameters()
    
    # Configurando parametros do solver
    solver.SetSolverSpecificParametersAsString("limits/gap=0.01, limits/time=30, " + \
                                               "limits/bestsol=20, " + \
                                               "heuristics/bound/onlywithoutsol=0, " + \
                                               "heuristics/bound/freq = 20")
    

    # Resolver o problema
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print('\nValor da funcao objetivo =', solver.Objective().Value())
        '''print('Solucao:')
        for v in range(n):
            if x[v].solution_value() > TOL:
                print(f'x{v} =', x[v].solution_value())'''
    else:
        print('O problema nao possui solucao.')

    print('Tempo de solucao: %f ms' % solver.wall_time())
    
    return solver


import random as rd
rd.seed(147)

n = 150
N = list(range(n))
g=[[] for _ in range(n)]

cont = 0
while cont < 0.5*(n*(n-1)/2):
    i = rd.choice(N)
    j = rd.choice(N)

    if i != j:
        if j not in g[i]:
            g[i].append(j)
            g[j].append(i)
            cont += 1

s = vertex_cover(g)
