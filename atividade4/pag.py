#UFC/DEMA, Programacao Inteira, 2023.1
# Problema de atribuicao generalizado -- Instancias aleatorias

#!pip install ortools
from ortools.linear_solver import pywraplp
import random as rd


def atribuicao_generalizado(m, n, A, c, b):
    TOL = 1.0e-6

    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        return

    solver.EnableOutput()
    
    # Criar variaveis
    x = [[solver.IntVar(0, 1, f'x{i}_{j}') for j in range(n)] for i in range(m)]

    # Restricoes
    for j in range(n):
        solver.Add( sum([x[i][j] for i in range(m)]) == 1 )

    for i in range(m):
        solver.Add( sum([x[i][j]*A[i][j] for j in range(n)]) <= b[i] )

    # Funcao objetivo e sentido de otimizacao
    solver.Minimize( sum([x[i][j]*c[i][j] for i in range(m) for j in range(n)]) )

    #solver.set_time_limit(5000)
    #solverParams = pywraplp.MPSolverParameters()
    
    # Configurando parametros do solver
    solver.SetSolverSpecificParametersAsString("limits/gap=0.01, limits/time=120, " + \
                                               #"limits/bestsol=20, " + \
                                               "heuristics/bound/onlywithoutsol=0, " + \
                                               "heuristics/bound/freq = 20")
    

    # Resolver o problema
    status = solver.Solve()
    print('Tempo de solucao: %f ms' % solver.wall_time())

    if status == pywraplp.Solver.OPTIMAL:
        print('\nValor da funcao objetivo =', solver.Objective().Value())
        #print('Solucao:')
        sol: list[list[float]] = []
        for i in range(m):
            sol.append([])
            for j in range(n):
                sol[i].append( x[i][j].solution_value() )
                if x[i][j].solution_value() > TOL:
                    pass #print(f'x{i}_{j} =', x[i][j].solution_value())
        return sol
    else:
        print('O problema nao possui solucao.')
        return None

def main():
    rd.seed(744)

    # Dimensoes do problema
    m = 25
    n = 200
    
    # Dados do problema:
    A = [[rd.randint(1,100)  for j in range(n)] for i in range(m)]
    c = [[rd.randint(1,100) for j in range(n)] for i in range(m)]
    b = [0.5*sum([A[i][rd.randint(0,n-1)] + A[i][rd.randint(0,n-1)]]) for i in range(m)]

    # Resolucao do modelo padrao para o PAG
    x = atribuicao_generalizado(m, n, A, c, b)

    return m, n, A, b, c, x


if __name__ == "__main__":
    main()


