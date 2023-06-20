#%%
import igraph as ig
import numpy as np
from ortools.linear_solver import pywraplp

#%%
def generate_graph(rng: np.random.Generator, n: int, density: float) -> ig.Graph:
    vertices = np.arange(n)
    adjacency = np.zeros((n, n))
    max_num_of_edges = n * (n - 1) / 2 
    for _ in range(round(density * max_num_of_edges)):
        while True:
            i, j = rng.choice(vertices, size=2, replace=False)
            if adjacency[i, j] == 0:
                adjacency[i, j], adjacency[j, i] = 1, 1
                break
    g = ig.Graph.Adjacency(adjacency, mode="undirected")
    g.vs['label'] = list(range(n))
    return g
        
#%%
def generate_vertex_cover_problem(g: ig.Graph) -> pywraplp.Solver | None:
    solver = pywraplp.Solver.CreateSolver('GLOP')
    if not solver:
        return
    
    solver.EnableOutput()

    n = len(g.vs)
    x = [ solver.IntVar(0, 1, f'x_{i}') for i in range(n)]

    adjacency = g.get_adjacency()
    for i in range(1, n):
        for j in range(0, i):
            if adjacency[i][j] == 1:
                if i < j: 
                    continue
                solver.Add(x[i] + x[j] >= 1,
                           f'x_{i} + x_{j} >= 1')
    
    return solver

def copy_solver(solver: pywraplp.Solver) -> pywraplp.Solver:
    vars: list[pywraplp.Variable] = solver.variables()
    constraints: list[pywraplp.Constraint] = solver.constraints()
    version: str = solver.SolverVersion()

#%%
def solve_bab_vertex_cover(
        solver: pywraplp.Solver
):
    vars: list[pywraplp.Variable] = solver.variables()
    solver.a
    

#%%
gg = generate_graph(np.random.default_rng(2023), 7, 0.5)
ig.plot(gg)
solverr = generate_vertex_cover_problem(gg)
for constraint in solverr.constraints():
    print(constraint.name())
solverr.Solve()
for var in solverr.variables():
    print(var.solution_value())
# %%
